#!/usr/bin/env python3
"""
Week 5: Panda 机械臂逆运动学入门示例
=====================================
正运动学 (FK) 和逆运动学 (IK) 的基本演示。

FK: 给定关节角度 → 计算末端位置 (确定性)
IK: 给定末端位置 → 求解关节角度 (可能有多个解)

运行方式:
  pip install pybullet numpy
  python3 panda_ik_demo.py
"""

import pybullet as p
import pybullet_data
import numpy as np
import time
import math


def fk_demo(robot_id, joint_indices):
    """
    正运动学演示:
    手动设置关节角度，观察末端位置变化
    """
    print("\n" + "=" * 50)
    print("📐 正运动学 (FK) 演示")
    print("=" * 50)

    # 测试几个不同的关节配置
    test_configs = [
        ("零位", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        ("前伸", [0.0, -0.4, 0.0, -1.5, 0.0, 1.0, 0.0]),
        ("上举", [0.0, -1.0, 0.0, -2.0, 0.0, 1.5, 0.0]),
        ("右偏", [0.5, -0.4, 0.0, -1.5, 0.0, 1.0, 0.0]),
    ]

    end_effector_idx = 11  # Panda hand

    for name, angles in test_configs:
        for i, joint_idx in enumerate(joint_indices):
            p.resetJointState(robot_id, joint_idx, targetValue=angles[i])

        # 仿真几步让关节到位
        for _ in range(100):
            p.stepSimulation()
            time.sleep(1.0 / 240.0)

        # 读取末端位置
        state = p.getLinkState(robot_id, end_effector_idx)
        pos = state[0]
        orn_euler = p.getEulerFromQuaternion(state[1])

        print(f"  {name}: 末端位置=({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}), "
              f"姿态=({math.degrees(orn_euler[0]):.1f}°, {math.degrees(orn_euler[1]):.1f}°, {math.degrees(orn_euler[2]):.1f}°)")

        time.sleep(2.0)


def ik_demo(robot_id, joint_indices):
    """
    逆运动学演示:
    指定目标位置，求解关节角度
    """
    print("\n" + "=" * 50)
    print("📐 逆运动学 (IK) 演示")
    print("=" * 50)

    end_effector_idx = 11

    # 测试目标: 机械臂前方不同位置
    test_targets = [
        ("正前方", [0.5, 0.0, 0.3]),
        ("左前方", [0.4, 0.2, 0.3]),
        ("右前方", [0.4, -0.2, 0.3]),
        ("偏高位置", [0.3, 0.0, 0.6]),
    ]

    target_orn = p.getQuaternionFromEuler([0, math.pi, 0])

    for name, target in test_targets:
        print(f"\n  目标: {name} {target}")

        ik_solution = p.calculateInverseKinematics(
            bodyUniqueId=robot_id,
            endEffectorLinkIndex=end_effector_idx,
            targetPosition=target,
            targetOrientation=target_orn,
            maxNumIterations=100,
            residualThreshold=1e-5
        )

        angles = ik_solution[:len(joint_indices)]
        print(f"  IK 解: {[f'{a:.3f}' for a in angles]}")

        # 移动机械臂到该位置
        for i, joint_idx in enumerate(joint_indices):
            p.setJointMotorControl2(
                bodyUniqueId=robot_id,
                jointIndex=joint_idx,
                controlMode=p.POSITION_CONTROL,
                targetPosition=angles[i],
                force=500.0
            )

        # 等待到位
        for _ in range(200):
            p.stepSimulation()
            time.sleep(1.0 / 240.0)

        # 验证末端位置
        actual_pos = p.getLinkState(robot_id, end_effector_idx)[0]
        error = math.sqrt(sum((a - t) ** 2 for a, t in zip(actual_pos, target)))
        print(f"  实际位置: ({actual_pos[0]:.3f}, {actual_pos[1]:.3f}, {actual_pos[2]:.3f}), "
              f"误差: {error*1000:.1f}mm")

        time.sleep(1.5)


def main():
    physics_client = p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.81)

    plane_id = p.loadURDF("plane.urdf")
    robot_id = p.loadURDF("franka_panda/panda.urdf", basePosition=[0, 0, 0], useFixedBase=True)

    # 获取可控关节
    num_joints = p.getNumJoints(robot_id)
    joint_indices = []
    for i in range(num_joints):
        info = p.getJointInfo(robot_id, i)
        if info[2] != p.JOINT_FIXED:
            joint_indices.append(i)

    print(f"🤖 Panda 机械臂: {len(joint_indices)} 个可控关节")

    # FK 演示
    fk_demo(robot_id, joint_indices)

    # IK 演示
    ik_demo(robot_id, joint_indices)

    print("\n✅ 演示完成。按 Ctrl+C 退出。")
    try:
        while p.isConnected():
            p.stepSimulation()
            time.sleep(1.0 / 60.0)
    except KeyboardInterrupt:
        p.disconnect()


if __name__ == '__main__':
    main()
