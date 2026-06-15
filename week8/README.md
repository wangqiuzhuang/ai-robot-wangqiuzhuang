# Week 8: ROS2 中级实践与工具链

## 本周概览

- ROS2 Launch 文件编写与多节点管理
- RViz2 3D 可视化配置
- ROS2 Bag 数据录制与回放
- 自定义 ROS2 消息与服务接口

---

## 1. ROS2 Launch 文件

### 为什么需要 Launch 文件？

手动启动多个 ROS2 节点需要打开多个终端，逐个运行 `ros2 run`。Launch 文件将节点启动、参数配置、生命周期管理集中到一个 Python 脚本中，一键启动整个系统。

### Python Launch 示例

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 节点1：小乌龟仿真器
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim',
            output='screen'
        ),
        # 节点2：键盘遥控
        Node(
            package='turtlesim',
            executable='turtle_teleop_key',
            name='teleop',
            prefix='xterm -e',  # 在新终端窗口打开
            output='screen'
        ),
    ])
```

### 运行 Launch 文件

```bash
# 方式1：直接运行 Python 文件
ros2 launch <package> <launch_file>

# 方式2：在包外运行
ros2 launch path/to/my_launch.py
```

---

## 2. RViz2 3D 可视化

RViz2 是 ROS2 的标准 3D 可视化工具，核心功能包括：

| 显示类型 | 对应话题 | 用途 |
|:---|:---|:---|
| **RobotModel** | `/robot_description` | 显示机器人 URDF 模型 |
| **TF** | `/tf` | 显示坐标帧和变换关系 |
| **LaserScan** | `/scan` | 显示2D激光雷达数据 |
| **PointCloud2** | `/points` | 显示3D点云 |
| **Image** | `/camera/image` | 显示相机图像 |
| **Path** | `/plan` | 显示规划路径 |
| **Odometry** | `/odom` | 显示里程计轨迹 |

### 基本使用

```bash
# 启动 RViz2
rviz2

# 配合 robot_state_publisher 显示机器人模型
ros2 launch urdf_tutorial display.launch.py model:=path/to/robot.urdf
```

### RViz2 配置要点

- **Fixed Frame**：必须设置为存在的坐标帧（通常 `map` 或 `odom`）
- **Topic 可靠性**：QoS 设置需与发布端匹配（Reliable vs Best Effort）
- **显示效率**：大量点云时可降低 Decay Time 减少渲染负担

---

## 3. ROS2 Bag 数据录制与回放

Bag 是 ROS2 的数据记录格式，相当于机器人系统的"行车记录仪"——录制传感器数据后，可离线反复回放和调试算法。

```bash
# 录制指定话题
ros2 bag record -o my_experiment /turtle1/pose /turtle1/cmd_vel

# 录制所有话题
ros2 bag record -a -o full_recording

# 查看 Bag 文件信息
ros2 bag info my_experiment

# 回放 Bag 数据（消息带上原始时间戳）
ros2 bag play my_experiment

# 回放并倍速（2x）
ros2 bag play my_experiment --rate 2.0
```

### 典型场景

1. 在真实机器人上录制一次传感器数据
2. 回到实验室后反复回放，离线调试感知/规划算法
3. 比对不同算法在同一数据上的表现

---

## 4. 自定义消息接口

### 创建自定义消息

在 ROS2 包中定义 `.msg` 文件：

```
# MySensor.msg
std_msgs/Header header  # 时间戳和 frame_id
int32 sensor_id
string sensor_name
float64[] readings
bool is_calibrated
```

### 配置 CMakeLists.txt 和 package.xml

```xml
<!-- package.xml -->
<build_depend>rosidl_default_generators</build_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
```

```cmake
# CMakeLists.txt
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/MySensor.msg"
)
```

### 编译和使用

```bash
colcon build --packages-select my_package
source install/setup.bash

# 查看生成的消息
ros2 interface show my_package/msg/MySensor
```

---

## 踩坑记录

| 问题 | 原因 | 解决方案 |
|:---|:---|:---|
| Launch 文件中节点启动后立刻退出 | 未设置 `output='screen'` 或节点缺少依赖 | 添加 `output='screen'` 查看日志，检查依赖安装 |
| RViz2 中不显示机器人模型 | `robot_description` 参数未设置 | `ros2 param get /rviz2 robot_description` 确认 |
| Bag 回放话题名不匹配 | 录制和播放时话题名不一致 | `ros2 bag play xxx --remap /old_topic:=/new_topic` |
| 自定义消息编译失败 | 缺少 rosidl 依赖 | `sudo apt install ros-humble-rosidl-default-generators` |

---

## 总结

本周掌握了 ROS2 中级工具链的使用：

1. **Launch 自动化**：一个命令启动整个机器人系统
2. **RViz2 可视化**：3D 实时显示机器人模型、传感器数据和导航路径
3. **Bag 数据管理**：录制-回放-分析的工作流，支持离线算法调试
4. **自定义接口**：扩展 ROS2 消息体系以满足项目特定需求

这些工具链构成了实际机器人项目开发的标准工程环境。
