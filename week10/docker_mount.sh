#!/bin/bash
# Week 10: Docker 卷挂载与双向同步脚本
# =======================================
# 将本地目录挂载到 Docker 容器，实现双向文件同步。
#
# 场景:
#   - 在本地 (Windows/WSL) 编辑 .py 文件
#   - 挂载到容器内 /home/ws
#   - 在容器中运行代码，结果自动反映到本地
#
# 使用方式:
#   chmod +x docker_mount.sh
#   ./docker_mount.sh

set -e

IMAGE="ghcr.io/tiryoh/ros2-desktop-vnc:humble"
PORT="${PORT:-6081}"
SHM_SIZE="512m"
CONTAINER_NAME="ros2-week10"
LOCAL_DIR="${PWD}"           # 本地当前目录
REMOTE_DIR="/home/ws"        # 容器内挂载点

echo "🐳 Week 10: Docker 卷挂载实验"
echo "================================"
echo ""
echo "📂 本地目录:  ${LOCAL_DIR}"
echo "📁 远程目录:  ${REMOTE_DIR}"
echo "🔗 同步模式:  双向 (本地 ↔ 容器)"
echo "🌐 访问端口:  http://127.0.0.1:${PORT}"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装!"
    exit 1
fi

# 清理旧容器
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "🧹 清理旧容器..."
    docker stop "${CONTAINER_NAME}" 2>/dev/null || true
    docker rm "${CONTAINER_NAME}" 2>/dev/null || true
fi

# 启动容器 (带卷挂载)
echo "🚀 启动容器并挂载本地目录..."
docker run \
    --name "${CONTAINER_NAME}" \
    -p "${PORT}:80" \
    --shm-size="${SHM_SIZE}" \
    --security-opt seccomp=unconfined \
    -v "${LOCAL_DIR}:${REMOTE_DIR}" \
    -d \
    "${IMAGE}"

# 等待就绪
sleep 3

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo ""
    echo "✅ 容器已启动! 卷挂载: ${LOCAL_DIR} ↔ ${REMOTE_DIR}"
    echo ""
    echo "📝 验证双向同步:"
    echo "   1. 本地创建文件: touch ${LOCAL_DIR}/test_sync.txt"
    echo "   2. 进入容器:      docker exec -it ${CONTAINER_NAME} bash"
    echo "   3. 查看同步:      ls ${REMOTE_DIR}/test_sync.txt"
    echo ""
    echo "🖥️  VNC 访问: http://127.0.0.1:${PORT}"
    echo ""
    echo "💡 提示: PowerShell 窗口关闭后连接会断开，"
    echo "   文件已保存在本地目录，容器变化需 docker commit 保存。"
else
    echo "❌ 启动失败!"
    docker logs "${CONTAINER_NAME}"
    exit 1
fi
