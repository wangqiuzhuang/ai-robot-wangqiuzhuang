#!/bin/bash
# Week 7: Docker ROS2 Desktop VNC 快速启动脚本
# ==============================================
# 一键拉取并启动 ROS2 桌面容器，浏览器访问即可使用。
#
# 使用方式:
#   chmod +x docker_run.sh
#   ./docker_run.sh
#
# 启动后浏览器打开: http://127.0.0.1:6080

set -e

IMAGE="ghcr.io/tiryoh/ros2-desktop-vnc:humble"
PORT=6080
SHM_SIZE="512m"
CONTAINER_NAME="ros2-desktop-week7"

echo "🐳 Week 7: Docker ROS2 Desktop VNC 启动脚本"
echo "============================================"
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装！请先安装 Docker Desktop 或 docker-ce。"
    echo "   Windows: https://www.docker.com/products/docker-desktop/"
    echo "   Linux:   sudo apt install docker.io"
    exit 1
fi

# 检查 Docker 服务是否运行
if ! docker info &> /dev/null; then
    echo "❌ Docker 服务未运行！请先启动 Docker Desktop 或执行:"
    echo "   sudo systemctl start docker"
    exit 1
fi

# 拉取镜像 (如果本地没有)
echo "📥 检查镜像 $IMAGE ..."
if ! docker image inspect "$IMAGE" &> /dev/null; then
    echo "   本地未找到，正在拉取..."
    docker pull "$IMAGE"
    echo "   ✅ 拉取完成"
else
    echo "   ✅ 镜像已存在"
fi

# 停止并移除同名旧容器 (如果存在)
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "🧹 清理旧容器 $CONTAINER_NAME ..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
fi

# 启动容器
echo ""
echo "🚀 启动 ROS2 Desktop VNC 容器..."
echo "   镜像:   $IMAGE"
echo "   端口:   $PORT → 容器内 80"
echo "   共享内存: $SHM_SIZE"
echo "   容器名:  $CONTAINER_NAME"
echo ""

docker run \
    --name "$CONTAINER_NAME" \
    -p "${PORT}:80" \
    --shm-size="$SHM_SIZE" \
    -d \
    "$IMAGE"

# 等待容器就绪
echo "⏳ 等待容器就绪..."
sleep 3

# 确认运行状态
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo ""
    echo "✅ 容器已成功启动!"
    echo ""
    echo "🌐 浏览器访问: http://127.0.0.1:${PORT}"
    echo "   进入 XFCE 桌面后，打开终端执行:"
    echo "     source /opt/ros/humble/setup.bash"
    echo "     ros2 run turtlesim turtlesim_node"
    echo ""
    echo "🧹 停止容器: docker stop $CONTAINER_NAME"
    echo "🔍 查看日志: docker logs $CONTAINER_NAME"
else
    echo "❌ 容器启动失败! 查看日志: docker logs $CONTAINER_NAME"
    exit 1
fi
