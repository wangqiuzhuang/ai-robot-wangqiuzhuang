# Week 9: 机器人仿真环境与实践

## 本周概览

- Gazebo 仿真环境搭建
- Webots 机器人仿真入门
- 机器人 URDF 模型加载与调试
- 仿真环境中的传感器配置

## 1. Gazebo 与 ROS2 集成

```bash
# 安装 Gazebo
sudo apt install ros-humble-gazebo-ros-pkgs

# 启动 Gazebo 空世界
ros2 launch gazebo_ros gazebo.launch.py

# 在 Gazebo 中生成机器人模型
ros2 launch gazebo_ros spawn_entity.py -file robot.urdf -entity my_robot
```

## 2. URDF 模型加载

URDF（Unified Robot Description Format）描述机器人的物理结构：

```xml
<?xml version="1.0"?>
<robot name="my_robot">
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.5 0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
  </link>
</robot>
```

## 3. 仿真传感器配置

在 Gazebo 中为机器人添加传感器：

```xml
<!-- 激光雷达 -->
<gazebo reference="laser_link">
  <sensor type="ray" name="laser_sensor">
    <ray>
      <scan>
        <horizontal>
          <samples>360</samples>
          <resolution>1</resolution>
          <min_angle>-1.570796</min_angle>
          <max_angle>1.570796</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>
        <max>10.0</max>
      </range>
    </ray>
  </sensor>
</gazebo>
```

## 总结

本周学习了 Gazebo 与 ROS2 的集成仿真流程，掌握了 URDF 模型文件的编写与加载，以及在仿真环境中配置传感器的方法，为后续四足机器人仿真实验做好了环境准备。
