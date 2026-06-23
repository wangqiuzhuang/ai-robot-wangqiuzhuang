#!/usr/bin/env python3
"""
Week 4: PyBullet Laikago 四足机器狗加载与控制
=============================================
加载 PyBullet 内置的 Laikago 四足机器人模型，实现关节控制和姿态调整。

Laikago 是由 Unitree 宇树科技开发的四足机器人:
  - 12 个关节 (每条腿 3 个自由度:髋关节侧摆、髋关节前摆、膝关节)
  - 自重约 22kg
  - PyBullet 提供了完整的 URDF 模型和运动学参数

核心操作:
  1. 加载模型到仿真环境
  2. 读取所有关节信息
  3. 修改关节角度 (放倒 / 站立)
  4. 力矩控制模式切换

运行方式:
  pip install pybullet
  python3 laikago_demo.py
"""

import pybullet as p
import pybullet_data
import time


def print_joint_info(robot_id):
    """打印所有关节的详细信息"""
    num_joints = p.getNumJoints(robot_id)
    print(f"\n📋 Laikago 关节信息 (共 {num_joints} 个关节):")
    print(f"{'ID':<4} {'名称':<30} {'类型':<12} {'范围':<20}")
    print("-" * 70)

    joint_types = {
        p.JOINT_REVOLUTE: "旋转",
        p.JOINT_PRISMATIC: "平移",
        p.JOINT_FIXED: "固定",
    }

    for i in range(num_joints):
        info = p.getJointInfo(robot_id, i)
        # info 结构: (index, name, type, qIndex, uIndex, flags,
        #              damping, friction, lowerLimit, upperLimit,
        #              maxForce, maxVelocity, linkName, jointAxis,
        #              parentFramePos, parentFrameOrn, parentIndex)
        name = info[1].decode('utf-8')
        jtype = joint_types.get(info[2], str(info[2]))
        lower = info[8]
        upper = info[9]
        print(f"{i:<4} {name:<30} {jtype:<12} [{lower:.2f}, {upper:.2f}]")


def reset_all_joints(robot_id):
    """将所有关节重置为 0 角度 (默认站立姿态)"""
    num_joints = p.getNumJoints(robot_id)
    for i in range(num_joints):
        p.resetJointState(robot_id, i, targetValue=0.0)
    print("✅ 所有关节已重置为 0° (默认站立姿态)")


def lay_down_robot(robot_id):
    """放倒机器狗 — 将所有旋转关节角度设为 0 并关闭力矩控制"""
    print("\n🔽 放倒机器狗...")
    num_joints = p.getNumJoints(robot_id)

    for i in range(num_joints):
        info = p.getJointInfo(robot_id, i)
        if info[2] == p.JOINT_REVOLUTE:  # 只处理旋转关节
            # 关闭位置控制 → 关节自由落体
            p.setJointMotorControl2(
                bodyUniqueId=robot_id,
                jointIndex=i,
                controlMode=p.VELOCITY_CONTROL,
                targetVelocity=0.0,
                force=0.0  # 零力矩 → 自由下落
            )
    time.sleep(2.0)
    print("✅ 机器狗已放倒")


def stand_up_robot(robot_id):
    """让机器狗站立 — 恢复位置控制"""
    print("\n🔼 让机器狗站立...")
    num_joints = p.getNumJoints(robot_id)

    for i in range(num_joints):
        info = p.getJointInfo(robot_id, i)
        if info[2] == p.JOINT_REVOLUTE:
            # 恢复位置控制，目标角度 = 0
            p.setJointMotorControl2(
                bodyUniqueId=robot_id,
                jointIndex=i,
                controlMode=p.POSITION_CONTROL,
                targetPosition=0.0,
                force=500.0
            )
    time.sleep(2.0)
    print("✅ 机器狗已站立")


def main():
    # ── 初始化 PyBullet ──
    physics_client = p.connect(p.GUI)  # 图形界面模式
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.81)  # 设置重力

    # 加载地面
    plane_id = p.loadURDF("plane.urdf")

    # ── 加载 Laikago 模型 ──
    print("🐕 加载 Laikago 四足机器人...")
    robot_start_pos = [0, 0, 0.5]  # 起始位置 (x, y, z)
    robot_start_orn = p.getQuaternionFromEuler([0, 0, 0])  # 朝向
    robot_id = p.loadURDF(
        "laikago/laikago_toes.urdf",
        basePosition=robot_start_pos,
        baseOrientation=robot_start_orn,
        useFixedBase=False
    )

    # ── 打印关节信息 ──
    print_joint_info(robot_id)

    # ── 仿真循环 ──
    print("\n⏱️  仿真运行中... (按 Ctrl+C 退出)")
    print("  操作序列: 站立 3s → 放倒 2s → 站立 3s")
    state = 0
    state_timer = time.time()

    try:
        while p.isConnected():
            p.stepSimulation()
            elapsed = time.time() - state_timer

            if state == 0 and elapsed > 3.0:
                lay_down_robot(robot_id)
                state = 1
                state_timer = time.time()

            elif state == 1 and elapsed > 2.0:
                stand_up_robot(robot_id)
                state = 2
                state_timer = time.time()

            elif state == 2 and elapsed > 3.0:
                break

            time.sleep(1.0 / 240.0)  # 240 Hz 仿真步长

    except KeyboardInterrupt:
        print("\n🛑 仿真已停止")

    finally:
        p.disconnect()


if __name__ == '__main__':
    main()
