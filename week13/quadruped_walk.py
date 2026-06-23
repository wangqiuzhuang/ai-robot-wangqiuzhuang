#!/usr/bin/env python3
"""
Week 13: 四足机器人 Trot 步态行走程序
======================================
使用 PyBullet 加载 Laikago 四足机器人，实现 Trot 对角步态。

Trot 步态原理:
  - 四条腿分为两组: (左前LF + 右后RH) 和 (右前RF + 左后LH)
  - 两组相位差 180°，一组抬起时另一组着地
  - 占空比 0.5 (每条腿 50% 时间着地)
  - 髋关节前后摆动 + 膝关节上下运动 = 前进推力

运行方式:
  pip install pybullet numpy
  python3 quadruped_walk.py
"""

import pybullet as p
import pybullet_data
import numpy as np
import time
import math


class QuadrupedWalk:
    """四足机器人 Trot 步态行走控制器"""

    def __init__(self):
        # 初始化 PyBullet
        self.physics_client = p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        p.setTimeStep(1.0 / 240.0)

        # 加载地面
        self.plane_id = p.loadURDF("plane.urdf")

        # 加载 Laikago 机器人
        start_pos = [0, 0, 0.3]
        start_orn = p.getQuaternionFromEuler([0, 0, 0])
        self.robot_id = p.loadURDF(
            "laikago/laikago_toes.urdf",
            basePosition=start_pos,
            baseOrientation=start_orn,
            useFixedBase=False,
        )

        # 关节映射: Laikago 12个关节 (每条腿3个)
        # 腿的顺序: FR, FL, RR, RL (前右/前左/后右/后左)
        # 每组关节: 0=侧摆(abduction), 1=髋(hip), 2=膝(knee)
        self.num_joints = p.getNumJoints(self.robot_id)

        # 步态参数
        self.gait_frequency = 1.5       # 步态频率 (Hz)
        self.hip_amplitude = 0.4        # 髋关节摆动幅度 (rad)
        self.knee_amplitude = 0.6       # 膝关节摆动幅度 (rad)
        self.step_height = 0.05         # 抬脚高度补偿
        self.duty_cycle = 0.5           # 占空比
        self.phase_offset = math.pi     # 两组腿的相位差 (180°)

        # 关节索引分组
        self.leg_groups = self._identify_legs()

        print("🐕 Laikago 四足机器人 Trot 步态行走")
        print(f"   频率: {self.gait_frequency} Hz")
        print(f"   髋振幅: {self.hip_amplitude} rad")
        print(f"   膝振幅: {self.knee_amplitude} rad")
        print(f"   步态类型: Trot (对角小跑)")

    def _identify_legs(self):
        """识别四条腿的关节索引分组"""
        # Laikago URDF 的关节命名模式:
        # FR_hip, FR_upper, FR_lower (前右)
        # FL_hip, FL_upper, FL_lower (前左)
        # RR_hip, RR_upper, RR_lower (后右)
        # RL_hip, RL_upper, RL_lower (后左)
        legs = {"FR": [], "FL": [], "RR": [], "RL": []}

        for i in range(self.num_joints):
            info = p.getJointInfo(self.robot_id, i)
            name = info[1].decode('utf-8')
            if info[2] != p.JOINT_FIXED:
                for prefix in ["FR", "FL", "RR", "RL"]:
                    if name.startswith(prefix) and i not in sum(legs.values(), []):
                        legs[prefix].append(i)

        # Trot 分组: 对角腿一组
        group_a = legs.get("FR", []) + legs.get("RL", [])  # 前右 + 后左
        group_b = legs.get("FL", []) + legs.get("RR", [])  # 前左 + 后右

        return {"group_a": group_a, "group_b": group_b}

    def compute_joint_angle(self, joint_idx, leg_phase, t):
        """
        计算单个关节的目标角度

        使用正弦波生成步态:
          hip(t)  = amplitude * sin(2π * freq * t + phase)
          knee(t) = amplitude * (sin(2π * freq * t + phase) * 0.5 + 0.3)

        膝关节在腿抬起时弯曲 (负角度)，着地时伸展 (小角度)
        """
        angle = 2 * math.pi * self.gait_frequency * t + leg_phase

        # 判断关节类型: 索引%3 == 0=侧摆, ==1=髋, ==2=膝
        joint_local_idx = joint_idx % 3

        if joint_local_idx == 0:
            # 侧摆关节: 小幅稳定
            return 0.0
        elif joint_local_idx == 1:
            # 髋关节: 正弦摆动 (产生前进推力)
            return self.hip_amplitude * math.sin(angle)
        else:
            # 膝关节: 配合髋关节运动
            # 当 sin(angle) > 0 时 (腿前摆)，膝盖弯曲让脚离地
            swing = math.sin(angle)
            if swing > 0:
                return -self.knee_amplitude * swing
            else:
                return -0.2  # 着地时轻微弯曲缓冲

    def apply_control(self, t: float):
        """应用当前时间步的控制指令"""
        all_joints = set()
        for indices in self.leg_groups.values():
            all_joints.update(indices)

        for joint_idx in all_joints:
            # 确定该关节属于哪个组
            if joint_idx in self.leg_groups["group_a"]:
                phase = 0
            else:
                phase = self.phase_offset  # B组落后180°

            target_angle = self.compute_joint_angle(joint_idx, phase, t)

            p.setJointMotorControl2(
                bodyUniqueId=self.robot_id,
                jointIndex=joint_idx,
                controlMode=p.POSITION_CONTROL,
                targetPosition=target_angle,
                force=500.0,
            )

    def run(self, duration: float = 30.0):
        """主循环"""
        start_time = time.time()
        step = 0

        print(f"\n▶️  开始行走 (时长 {duration}s)... 按 Ctrl+C 提前退出")

        try:
            while time.time() - start_time < duration:
                t = time.time() - start_time

                # 应用步态控制
                self.apply_control(t)

                # 推进仿真
                p.stepSimulation()

                step += 1
                if step % 240 == 0:  # 每秒输出一次
                    pos, _ = p.getBasePositionAndOrientation(self.robot_id)
                    vel, _ = p.getBaseVelocity(self.robot_id)
                    print(f"  t={t:.1f}s | 位置=({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}) | "
                          f"速度=({vel[0]:.3f}, {vel[1]:.3f})")

                time.sleep(1.0 / 240.0)

        except KeyboardInterrupt:
            print("\n🛑 行走已停止")

        finally:
            pos, _ = p.getBasePositionAndOrientation(self.robot_id)
            print(f"\n✅ 行走完成: 机器人最终位置 ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f})")
            print(f"   总步数: {step}")
            p.disconnect()


def main():
    walker = QuadrupedWalk()

    # 等待物理稳定
    print("⏳ 等待物理稳定...")
    for _ in range(500):
        p.stepSimulation()
        time.sleep(1.0 / 240.0)

    walker.run(duration=20.0)


if __name__ == '__main__':
    main()
