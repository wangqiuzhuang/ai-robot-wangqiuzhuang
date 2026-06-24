# Week 9: 机器人仿真环境与实践

## 本周概览

- Gazebo 3D 仿真环境搭建与 ROS2 集成
- Webots 跨平台机器人仿真入门
- 机器人 URDF 模型加载与调试
- 仿真环境中传感器（LiDAR、相机、IMU）的配置与测试

---

## 1. Gazebo 与 ROS2 集成

Gazebo 是目前 ROS 生态中最成熟的 3D 物理仿真环境，支持刚体动力学、传感器仿真和多种机器人模型。

### 安装与启动

```bash
# 安装 Gazebo 与 ROS2 集成包
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros2-control

# 启动 Gazebo 空世界
ros2 launch gazebo_ros gazebo.launch.py

# 启动带地面和光照的默认世界
ros2 launch gazebo_ros empty_world.launch.py
```

### 在 Gazebo 中生成机器人

```bash
# 从 URDF 文件生成机器人
ros2 run gazebo_ros spawn_entity.py \
  -file robot.urdf \
  -entity my_robot \
  -x 0 -y 0 -z 0.5
```

### Gazebo vs Webots 对比

| 维度 | Gazebo | Webots |
|:---|:---|:---|
| ROS 集成 | 最成熟，`gazebo_ros_pkgs` | 良好，`webots_ros2` |
| 物理引擎 | ODE / Bullet / DART / Simbody | 自有 ODE 分支 |
| 模型库 | Gazebo Model Database | 丰富的预置模型库 |
| 学习曲线 | 中等 | 较平缓 |
| 适用场景 | 学术研究、ROS 项目 | 教育、快速原型 |
| 平台支持 | 仅 Linux | Windows / macOS / Linux |

---

## 2. URDF 模型编写与加载

URDF (Unified Robot Description Format) 是 XML 格式的机器人模型描述标准：

```xml
<?xml version="1.0"?>
<robot name="my_robot">
  <!-- 基座连杆 -->
  <link name="base_link">
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.1" ixy="0.0" ixz="0.0"
               iyy="0.1" iyz="0.0" izz="0.1"/>
    </inertial>
    <visual>
      <geometry>
        <box size="0.5 0.5 0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.5 0.5 0.2"/>
      </geometry>
    </collision>
  </link>

  <!-- 轮子关节 -->
  <joint name="base_to_wheel" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_link"/>
    <origin xyz="0.15 0.2 -0.05" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
  </joint>
</robot>
```

### URDF 元素详解

| 元素 | 必须 | 说明 |
|:---|:---|:---|
| `<link>` | ✅ | 机器人的刚性部件，需定义质量、惯性和几何形状 |
| `<joint>` | ✅ | 连接两个连杆，定义运动类型和范围 |
| `<inertial>` | ✅ | 质量 + 惯性矩阵，物理仿真必需 |
| `<visual>` | 否 | 可视化用的几何体（不影响仿真） |
| `<collision>` | 否 | 碰撞检测几何体（影响物理仿真，可简化） |

### 调试技巧

```bash
# 检查 URDF 语法
check_urdf robot.urdf

# 可视化 URDF 结构
urdf_to_graphviz robot.urdf | dot -Tpng > robot_structure.png

# 在 RViz2 中查看
ros2 launch urdf_tutorial display.launch.py model:=robot.urdf
```

---

## 3. 仿真传感器配置

### 激光雷达 (LiDAR)

```xml
<gazebo reference="laser_link">
  <sensor type="ray" name="lidar">
    <ray>
      <scan>
        <horizontal>
          <samples>360</samples>     <!-- 每圈360个采样点 -->
          <resolution>1</resolution>  <!-- 1度角分辨率 -->
          <min_angle>-1.570796</min_angle>
          <max_angle>1.570796</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>    <!-- 最小探测距离 (m) -->
        <max>10.0</max>   <!-- 最大探测距离 (m) -->
      </range>
    </ray>
    <plugin name="lidar_plugin" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <namespace>/robot</namespace>
        <remapping>~/out:=scan</remapping>
      </ros>
    </plugin>
  </sensor>
</gazebo>
```

### RGB 相机

```xml
<gazebo reference="camera_link">
  <sensor type="camera" name="camera">
    <camera>
      <horizontal_fov>1.047</horizontal_fov>
      <image>
        <width>640</width>
        <height>480</height>
      </image>
    </camera>
    <plugin name="camera_plugin" filename="libgazebo_ros_camera.so">
      <ros><namespace>/robot</namespace></ros>
    </plugin>
  </sensor>
</gazebo>
```

---

## 踩坑记录

| 问题 | 原因 | 解决方案 |
|:---|:---|:---|
| Gazebo 启动后闪退 | GPU 驱动不兼容 / 缺少依赖 | `sudo apt install ros-humble-gazebo-*` 完整安装 |
| URDF 模型在 Gazebo 中不动 | 缺少 `<inertial>` 标签 | 为每个 `<link>` 添加质量和惯性参数 |
| 传感器话题无数据 | 插件未正确加载 | 检查 `filename` 中的 `.so` 文件名是否与实际一致 |
| Gazebo 渲染卡顿 | 使用软件渲染 | 设置环境变量 `export LIBGL_ALWAYS_SOFTWARE=1` |
| Webots 模型不显示 | 缺少 PROTO 文件 | 确保 `.proto` 文件在 `WEBOTS_HOME` 路径中 |

---

## 总结

本周建立了完整的机器人仿真环境能力：

1. **Gazebo 集成**：完成了 ROS2 与 Gazebo 的桥接，实现模型加载和传感器仿真
2. **URDF 建模**：掌握了从零编写和调试机器人模型文件的技能
3. **传感器配置**：学会了在仿真环境中添加 LiDAR、相机等传感器并进行数据采集
4. **工具对比**：理解了 Gazebo 和 Webots 的各自优势与适用场景

这些仿真能力为 Week 12-13 的四足机器人步态规划和强化学习实验提供了虚拟测试环境。

## 作业截图

![Gazebo仿真环境](img/gazebo_world.png)
![URDF模型可视化](img/urdf_rviz.png)

## 代码说明

**`check_urdf.py`** — URDF 模型语法检查工具
- 解析 URDF XML 文件，验证基本结构
- 检查每个 `<link>` 是否有惯性参数 `<inertial>`
- 验证 `<joint>` 的 parent/child 引用是否正确
- 输出 robots name、links/joints 数量及错误/警告

**`empty_world.sdf`** — Gazebo 仿真世界配置文件
- 包含地面、光照、重力 (9.81 m/s²)
- 使用 ODE 物理引擎，1ms 步长
- 可作为自定义仿真环境的起点

## 运行方式

```bash
cd week9

# URDF 检查 (检查 week8 的机器人模型)
python3 check_urdf.py ../week8/my_robot.urdf

# Gazebo 启动
gazebo empty_world.sdf

# 或者 ROS2 方式启动
ros2 launch gazebo_ros gazebo.launch.py world:=./empty_world.sdf
```
