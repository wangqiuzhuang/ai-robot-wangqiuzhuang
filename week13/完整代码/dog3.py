import pybullet as p
import pybullet_data
import time
import math

def main():
    p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.8)
    p.setTimeStep(1/500)
    
    p.loadURDF("plane.urdf")
    
    robot = p.loadURDF(
        "laikago/laikago_toes_zup.urdf",
        [0, 0, 0.5],
        [0, 0, 1, 0]
    )
    
    joints = {
        'FR_hip': 0, 'FR_upper': 1, 'FR_lower': 2, 'FR_toe': 3,
        'FL_hip': 4, 'FL_upper': 5, 'FL_lower': 6, 'FL_toe': 7,
        'RR_hip': 8, 'RR_upper': 9, 'RR_lower': 10, 'RR_toe': 11,
        'RL_hip': 12, 'RL_upper': 13, 'RL_lower': 14, 'RL_toe': 15,
    }
    
    base_pose = {
        'FR_hip': 0.0, 'FR_upper': -0.2, 'FR_lower': -0.3, 'FR_toe': -0.1,
        'FL_hip': 0.0, 'FL_upper': -0.2, 'FL_lower': -0.3, 'FL_toe': -0.1,
        'RR_hip': 0.0, 'RR_upper': -0.2, 'RR_lower': -0.3, 'RR_toe': -0.1,
        'RL_hip': 0.0, 'RL_upper': -0.2, 'RL_lower': -0.3, 'RL_toe': -0.1,
    }
    
    print("初始化站立...")
    for joint_name, angle in base_pose.items():
        p.resetJointState(robot, joints[joint_name], angle)
    
    for step in range(500):
        for joint_name, angle in base_pose.items():
            p.setJointMotorControl2(robot, joints[joint_name], p.POSITION_CONTROL,
                                   targetPosition=angle, force=30, positionGain=0.15)
        p.stepSimulation()
        time.sleep(0.002)
    
    print("✓ 站立成功！开始稳定行走...")
    time.sleep(1)
    
    p.resetDebugVisualizerCamera(cameraDistance=2.0, cameraYaw=45, cameraPitch=-30, 
                                 cameraTargetPosition=[0, 0, 0.3])
    
    # 经过验证的稳定参数
    step_amp = 0.06       # 步幅（0.06稳定，0.08以上会倒）
    step_freq = 2.0       # 步频
    forward_bias = 0.03   # 前进偏移
    
    t = 0.0
    dt = 1/240
    start_pos = [0, 0]
    last_stable_t = 0
    
    # 尝试逐步增加参数的阶段
    phases = [
        {'duration': 15, 'amp': 0.06, 'freq': 2.0, 'bias': 0.030, 'name': '稳定慢走'},
        {'duration': 15, 'amp': 0.07, 'freq': 2.2, 'bias': 0.035, 'name': '稍快步走'},
        {'duration': 15, 'amp': 0.08, 'freq': 2.5, 'bias': 0.040, 'name': '正常步走'},
        {'duration': 15, 'amp': 0.09, 'freq': 2.8, 'bias': 0.045, 'name': '快速走(小心)'},
    ]
    
    print("\n=== 渐进式行走测试 ===")
    print("将在不同阶段尝试不同参数")
    print("如果摔倒会自动降级到上一个稳定参数")
    print("=========================\n")
    
    current_phase = 0
    phase_start_t = 0
    
    try:
        while t < 60:  # 运行60秒
            # 确定当前阶段
            elapsed = t - phase_start_t
            
            if current_phase < len(phases):
                phase_info = phases[current_phase]
                if elapsed > phase_info['duration']:
                    current_phase += 1
                    phase_start_t = t
                    if current_phase < len(phases):
                        phase_info = phases[current_phase]
                        print(f"\n{t:.0f}秒: 进入「{phase_info['name']}」阶段")
                        print(f"  步幅={phase_info['amp']:.2f}, 步频={phase_info['freq']:.1f}Hz")
                    else:
                        print(f"\n{t:.0f}秒: 测试结束，保持最后稳定参数")
                        break
            
            # 使用当前阶段参数
            if current_phase < len(phases):
                phase_info = phases[current_phase]
                step_amp = phase_info['amp']
                step_freq = phase_info['freq']
                forward_bias = phase_info['bias']
            
            # 生成步态
            motion_pose = base_pose.copy()
            phase_angle = t * step_freq * 2 * math.pi
            
            # 对角小跑步态
            upper_offset = step_amp * math.sin(phase_angle)
            lower_offset = step_amp * 0.5 * math.sin(phase_angle)
            
            # FR和RL对角组
            motion_pose['FR_upper'] += upper_offset
            motion_pose['FR_lower'] += lower_offset
            motion_pose['RL_upper'] += upper_offset
            motion_pose['RL_lower'] += lower_offset
            
            # FL和RR对角组（反相）
            motion_pose['FL_upper'] -= upper_offset
            motion_pose['FL_lower'] -= lower_offset
            motion_pose['RR_upper'] -= upper_offset
            motion_pose['RR_lower'] -= lower_offset
            
            # 前进偏移
            motion_pose['RR_upper'] -= forward_bias
            motion_pose['RL_upper'] -= forward_bias
            
            # 应用控制
            for joint_name, target_angle in motion_pose.items():
                joint_id = joints[joint_name]
                p.setJointMotorControl2(
                    robot, joint_id,
                    p.POSITION_CONTROL,
                    targetPosition=target_angle,
                    force=50,
                    positionGain=0.25,
                    velocityGain=0.1
                )
            
            p.stepSimulation()
            
            # 状态监控
            pos, ori = p.getBasePositionAndOrientation(robot)
            euler = p.getEulerFromQuaternion(ori)
            vel, _ = p.getBaseVelocity(robot)
            speed = math.sqrt(vel[0]**2 + vel[1]**2)
            
            # 计算距离
            dx = pos[0] - start_pos[0]
            dy = pos[1] - start_pos[1]
            distance = math.sqrt(dx**2 + dy**2)
            
            # 实时显示
            if int(t * 10) % 5 == 0:
                phase_name = phases[min(current_phase, len(phases)-1)]['name']
                print(f"\r{phase_name:6s} | {t:5.1f}s | 幅:{step_amp:.2f} 频:{step_freq:.1f} | 高:{pos[2]:.2f} 速:{speed:.2f} | 距离:{distance:.2f}m", end='')
            
            # 不稳定检测
            if pos[2] < 0.25 or abs(euler[0]) > 0.6:
                print(f"\n⚠ {t:.1f}秒: 不稳定！回退到上一阶段...")
                
                # 回退到上一个稳定参数
                if current_phase > 0:
                    current_phase -= 1
                    phase_info = phases[current_phase]
                    step_amp = phase_info['amp']
                    step_freq = phase_info['freq']
                    forward_bias = phase_info['bias']
                    phase_start_t = t
                    print(f"回退到「{phase_info['name']}」: 幅={step_amp:.2f} 频={step_freq:.1f}")
                
                # 恢复站立
                for _ in range(300):
                    for joint_name, angle in base_pose.items():
                        p.setJointMotorControl2(robot, joints[joint_name], p.POSITION_CONTROL,
                                               targetPosition=angle, force=60, positionGain=0.3)
                    p.stepSimulation()
                    time.sleep(0.002)
                
                print("已恢复，继续行走...")
                time.sleep(0.5)
            
            # 相机跟随
            if int(t * 4) % 8 == 0:
                p.resetDebugVisualizerCamera(
                    cameraDistance=2.0, cameraYaw=45 + t * 3, cameraPitch=-25,
                    cameraTargetPosition=[pos[0], pos[1], pos[2] + 0.3]
                )
            
            time.sleep(dt)
            t += dt
            
    except KeyboardInterrupt:
        pass
    
    finally:
        pos, _ = p.getBasePositionAndOrientation(robot)
        dx = pos[0] - start_pos[0]
        dy = pos[1] - start_pos[1]
        total_distance = math.sqrt(dx**2 + dy**2)
        avg_speed = total_distance / t if t > 0 else 0
        
        print(f"\n\n{'='*50}")
        print(f"  行走测试总结")
        print(f"{'='*50}")
        print(f"  总时间: {t:.1f}秒")
        print(f"  总距离: {total_distance:.2f}米")
        print(f"  平均速度: {avg_speed:.3f} m/s ({avg_speed*3.6:.1f} km/h)")
        print(f"  最终位置: ({pos[0]:.2f}, {pos[1]:.2f})")
        print(f"  最后稳定参数: 步幅={step_amp:.2f} 步频={step_freq:.1f}Hz")
        print(f"{'='*50}")
        p.disconnect()

if __name__ == "__main__":
    main()