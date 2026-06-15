# Week 8: ROS2 中级实践与工具链

## 本周概览

- ROS2 Launch 文件编写
- RViz2 可视化配置
- ROS2 Bag 数据记录与回放
- 自定义 ROS2 消息接口

## 1. ROS2 Launch 文件

Launch 文件用于同时启动多个 ROS2 节点，支持参数配置和节点生命周期管理。

### Python Launch 示例

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim'
        ),
        Node(
            package='turtlesim',
            executable='turtle_teleop_key',
            name='teleop',
            prefix='xterm -e'
        )
    ])
```

## 2. RViz2 可视化

RViz2 是 ROS2 的标准 3D 可视化工具，用于显示机器人模型、传感器数据和 TF 坐标变换。

```bash
# 启动 RViz2
rviz2

# 配合 robot_state_publisher 使用
ros2 launch urdf_tutorial display.launch.py model:=path/to/urdf
```

## 3. ROS2 Bag 数据录制与回放

```bash
# 录制指定话题
ros2 bag record -o my_bag /topic1 /topic2

# 查看 bag 信息
ros2 bag info my_bag

# 回放 bag 数据
ros2 bag play my_bag
```

## 4. 自定义消息接口

创建自定义 `.msg` 文件：

```msg
# MyCustom.msg
int32 id
string name
float64[] values
```

## 总结

本周掌握了 ROS2 中级工具链的使用，包括 Launch 文件自动化节点管理、RViz2 3D 可视化、Bag 数据录制回放以及自定义消息接口的定义，为后续复杂机器人系统开发提供了工程化基础。
