#!/usr/bin/env python3
"""
Week 8: ROS2 Launch 文件 — 小乌龟多节点启动
============================================
一键启动 turtlesim 仿真器 + 键盘遥控 + 自定义控制器。

Launch 文件优势:
  - 替代手动打开多个终端逐一 ros2 run
  - 集中管理参数、重映射、生命周期
  - 支持条件启动和参数化配置

运行方式:
  cd week8
  ros2 launch turtlesim_launch.py
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """生成 Launch 描述，启动 3 个节点"""

    # 声明启动参数
    turtle_name_arg = DeclareLaunchArgument(
        'turtle_name',
        default_value='turtle1',
        description='小乌龟的名称'
    )

    use_keyboard_arg = DeclareLaunchArgument(
        'use_keyboard',
        default_value='true',
        description='是否启动键盘遥控'
    )

    # 节点1: 小乌龟仿真器
    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='sim',
        output='screen',
        parameters=[{
            'background_r': 0,
            'background_g': 0,
            'background_b': 0,
        }],
        remappings=[],
    )

    # 节点2: 键盘遥控 (可选)
    keyboard_node = Node(
        package='turtlesim',
        executable='turtle_teleop_key',
        name='teleop_keyboard',
        prefix='xterm -e',  # 在新终端窗口打开
        output='screen',
        condition=None,  # 后面会设置条件
    )

    # 节点3: 自定义画圆控制器
    # 注意: 这个节点需要放在 ROS2 包中或作为独立 Python 脚本运行
    # 这里展示 Launch 文件的配置方式
    controller_node = Node(
        package='turtlesim',
        executable='draw_square',  # turtlesim 自带的示例
        name='square_controller',
        output='screen',
    )

    return LaunchDescription([
        turtle_name_arg,
        use_keyboard_arg,
        LogInfo(msg=['🐢 启动 turtlesim 多节点系统...']),
        turtlesim_node,
        keyboard_node,
        # controller_node,  # 取消注释以启用自动控制器
    ])
