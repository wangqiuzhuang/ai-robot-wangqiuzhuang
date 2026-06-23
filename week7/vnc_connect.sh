#!/bin/bash
# Week 7: VNC 远程桌面连接脚本
# ==============================
# 用于连接运行中的 ROS2 Desktop VNC 容器。
#
# 使用方式:
#   chmod +x vnc_connect.sh
#   ./vnc_connect.sh

set -e

PORT=${1:-6080}
CONTAINER_NAME="ros2-desktop-week7"

echo "🔌 Week 7: VNC 远程桌面连接"
echo "============================"

# 检查容器是否在运行
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "✅ 容器 $CONTAINER_NAME 正在运行"
    echo ""
    echo "访问方式:"
    echo "  浏览器: http://127.0.0.1:${PORT}"
    echo ""
    echo "常用 ROS2 命令 (在容器终端中执行):"
    echo "  source /opt/ros/humble/setup.bash"
    echo "  ros2 run turtlesim turtlesim_node &"
    echo "  ros2 run turtlesim turtle_teleop_key"
    echo ""
    echo "容器内文件位置:"
    echo "  ROS2 安装: /opt/ros/humble/"
    echo "  工作目录:   /home/ubuntu/"
else
    echo "❌ 容器未运行！请先执行: ./docker_run.sh"
    echo ""
    echo "或者手动启动已有容器:"
    echo "  docker start $CONTAINER_NAME"
    exit 1
fi
