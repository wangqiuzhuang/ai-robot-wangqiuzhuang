#!/usr/bin/env python3
"""
Week 5: Panda 机械臂逆运动学轨迹控制
=====================================
使用 PyBullet 的 Panda (Franka Emika) 机械臂模型，
通过逆运动学 (IK) 计算关节角度，实现末端画圆轨迹。

核心概念:
  - 正运动学 (FK): 关节角度 θ → 末端位置 (x, y, z)
  - 逆运动学 (IK): 末端位置 (x, y, z) → 关节角度 θ
  - 笛卡尔轨迹规划: 在任务空间规划路径 → IK 求解 → 关节空间执行

机械臂参数:
  - Panda 7 自由度机械臂
  - 工作半径约 0.85m
  - PyBullet 提供了内置的 IK 求解器

运行方式:
  pip install pybullet numpy
  python3 panda_circle.py
"""

import pybullet as p
import pybullet_data
import numpy as np
import time
import math


class PandaCircleDemo:
    """Panda 机械臂画圆演示"""

    def __init__(self):
        # 初始化仿真
        self.physics_client = p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)

        # 加载地面和 Panda 模型
        self.plane_id = p.loadURDF("plane.urdf")
        self.robot_id = p.loadURDF(
            "franka_panda/panda.urdf",
            basePosition=[0, 0, 0],
            useFixedBase=True
        )

        # 获取末端执行器索引 (最后一个关节之后的 link)
        self.end_effector_index = 11  # Panda hand link

        # 关节数量和信息
        self.num_joints = p.getNumJoints(self.robot_id)
        self.joint_indices = self._get_controllable_joints()

        print(f"🤖 Panda 机械臂: {len(self.joint_indices)} 个可控关节")
        print(f"📍 末端执行器索引: {self.end_effector_index}")

        # 圆心和半径参数
        self.circle_center = [0.4, 0.0, 0.4]  # (x, y, z) — 在机械臂前方
        self.circle_radius = 0.1               # 半径 10cm
        self.num_waypoints = 100               # 轨迹点数

        # 当前关节角度
        self.joint_angles = None
        self._reset_to_home()

    def _get_controllable_joints(self):
        """获取可控制的关节索引"""
        joints = []
        for i in range(self.num_joints):
            info = p.getJointInfo(self.robot_id, i)
            if info[2] != p.JOINT_FIXED:  # 排除固定关节
                joints.append(i)
        return joints

    def _reset_to_home(self):
        """将机械臂移动到初始姿态"""
        # Panda 的默认零位是一个合理的初始姿态
        self.joint_angles = [0.0] * len(self.joint_indices)
        for i, joint_idx in enumerate(self.joint_indices):
            p.resetJointState(self.robot_id, joint_idx, targetValue=0.0)
        time.sleep(1.0)
        print("✅ 机械臂已归位")

    def solve_ik(self, target_pos, target_orn=None):
        """
        逆运动学求解

        参数:
          target_pos: 目标末端位置 [x, y, z]
          target_orn: 目标末端姿态四元数 (默认保持当前姿态)

        返回:
          关节角度列表 (成功) 或 None (失败)
        """
        if target_orn is None:
            # 默认保持末端垂直向下 (适合抓取姿态)
            target_orn = p.getQuaternionFromEuler([0, math.pi, 0])

        joint_positions = p.calculateInverseKinematics(
            bodyUniqueId=self.robot_id,
            endEffectorLinkIndex=self.end_effector_index,
            targetPosition=target_pos,
            targetOrientation=target_orn,
            lowerLimits=[-2.8973, -1.7628, -2.8973, -3.0718, -2.8973, -0.0175, -2.8973],
            upperLimits=[2.8973, 1.7628, 2.8973, -0.0698, 2.8973, 3.7525, 2.8973],
            jointRanges=[5.8, 3.5, 5.8, 3.0, 5.8, 3.8, 5.8],
            restPoses=[0, 0, 0, -1.5, 0, 1.5, 0],
            maxNumIterations=100,
            residualThreshold=1e-5
        )

        return joint_positions[:len(self.joint_indices)]

    def move_to_position(self, target_pos, steps=50):
        """
        平滑移动到目标位置

        使用线性插值在关节空间中平滑过渡，避免抖动。
        """
        ik_solution = self.solve_ik(target_pos)
        if ik_solution is None:
            print(f"⚠️  IK 求解失败: {target_pos}")
            return False

        start_angles = np.array(self.joint_angles)
        end_angles = np.array(ik_solution)

        for t in range(steps):
            alpha = (t + 1) / steps  # 插值系数 [0, 1]
            # 使用平滑的缓动函数
            alpha_smooth = alpha * alpha * (3 - 2 * alpha)  # smoothstep
            interp_angles = start_angles + (end_angles - start_angles) * alpha_smooth

            for i, joint_idx in enumerate(self.joint_indices):
                p.setJointMotorControl2(
                    bodyUniqueId=self.robot_id,
                    jointIndex=joint_idx,
                    controlMode=p.POSITION_CONTROL,
                    targetPosition=interp_angles[i],
                    force=500.0
                )

            p.stepSimulation()
            time.sleep(1.0 / 240.0)

        self.joint_angles = end_angles.tolist()
        return True

    def draw_circle(self):
        """
        指挥机械臂末端沿圆形轨迹运动

        步骤:
          1. 在笛卡尔空间中生成圆周上的 100 个点
          2. 对每个点求解 IK
          3. 平滑过渡到每个目标点
        """
        print(f"\n⭕ 开始画圆: 圆心={self.circle_center}, 半径={self.circle_radius}m")
        print(f"   轨迹点数: {self.num_waypoints}")

        success_count = 0
        fail_count = 0

        for i, angle in enumerate(np.linspace(0, 2 * math.pi, self.num_waypoints)):
            # 计算圆周上的目标点
            target_x = self.circle_center[0] + self.circle_radius * math.cos(angle)
            target_y = self.circle_center[1] + self.circle_radius * math.sin(angle)
            target_z = self.circle_center[2]
            target_pos = [target_x, target_y, target_z]

            # 执行移动
            if self.move_to_position(target_pos, steps=10):
                success_count += 1
            else:
                fail_count += 1

            # 每 10 个点输出进度
            if (i + 1) % 10 == 0:
                current_pos = p.getLinkState(self.robot_id, self.end_effector_index)[0]
                error = math.sqrt(
                    (current_pos[0] - target_x) ** 2 +
                    (current_pos[1] - target_y) ** 2 +
                    (current_pos[2] - target_z) ** 2
                )
                print(f"  进度 {i+1}/{self.num_waypoints}: "
                      f"目标={(target_x:.3f}, {target_y:.3f}, {target_z:.3f}), "
                      f"跟踪误差={error*1000:.1f}mm")

        print(f"\n✅ 画圆完成: 成功 {success_count}/{self.num_waypoints}, 失败 {fail_count}")
        return success_count, fail_count

    def run(self):
        """主运行流程"""
        print("\n" + "=" * 60)
        print("Panda 机械臂逆运动学画圆实验")
        print("=" * 60)

        # 先让末端移动到圆周起点上方
        start_x = self.circle_center[0] + self.circle_radius
        start_pos = [start_x, self.circle_center[1], self.circle_center[2]]
        print(f"📍 移动到圆起点: {start_pos}")
        self.move_to_position(start_pos, steps=80)

        # 画圆
        success, fail = self.draw_circle()

        # 保持窗口打开
        print("\n⏸️  仿真完成。按 Ctrl+C 退出。")
        try:
            while p.isConnected():
                p.stepSimulation()
                time.sleep(1.0 / 60.0)
        except KeyboardInterrupt:
            pass
        finally:
            p.disconnect()


def main():
    demo = PandaCircleDemo()
    demo.run()


if __name__ == '__main__':
    main()
