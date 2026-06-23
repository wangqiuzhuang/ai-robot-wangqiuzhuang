#!/bin/bash
# Week 11: Docker 镜像持久化脚本
# =================================
# 将当前容器的状态保存为新的 Docker 镜像，实现环境持久化。
#
# 使用方式:
#   1. 先在容器中安装所需包 (pybullet, opencv, numpy等)
#   2. 执行 ./docker_commit.sh <容器ID> <新镜像名>
#
# 示例:
#   ./docker_commit.sh 9b76cfdb3097 wangqiuzhuang/ros2-custom
#
# 关键概念:
#   - 容器: 运行中的实例 (临时)
#   - 镜像: 保存的状态 (持久)
#   - docker commit: 将容器的当前状态"刻录"为镜像

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_banner() {
    echo -e "${GREEN}=================================${NC}"
    echo -e "${GREEN}  Docker 镜像持久化工具${NC}"
    echo -e "${GREEN}=================================${NC}"
    echo ""
}

show_containers() {
    echo -e "${YELLOW}📋 当前运行中的容器:${NC}"
    echo ""
    docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || true
    echo ""
}

do_commit() {
    local CONTAINER_ID="$1"
    local NEW_IMAGE="$2"
    local AUTHOR="${3:-wangqiuzhuang}"
    local MESSAGE="${4:-install pybullet opencv and dependencies}"

    # 验证容器存在
    if ! docker ps -a --format '{{.ID}}' | grep -q "^${CONTAINER_ID}"; then
        echo -e "${RED}❌ 容器 ${CONTAINER_ID} 不存在!${NC}"
        echo ""
        echo "可用容器:"
        docker ps -a --format "  {{.ID}} - {{.Image}} - {{.Names}}"
        exit 1
    fi

    echo -e "${YELLOW}💾 正在保存容器为镜像...${NC}"
    echo "   容器ID:   ${CONTAINER_ID}"
    echo "   新镜像名:  ${NEW_IMAGE}"
    echo "   作者:      ${AUTHOR}"
    echo "   描述:      ${MESSAGE}"
    echo ""

    docker commit \
        -m "${MESSAGE}" \
        -a "${AUTHOR}" \
        "${CONTAINER_ID}" \
        "${NEW_IMAGE}"

    echo ""
    echo -e "${GREEN}✅ 镜像保存成功!${NC}"
    echo ""
    echo "验证:"
    echo "  docker images | grep ${NEW_IMAGE}"
    echo ""
    echo "使用新镜像启动容器:"
    echo "  docker run -p 6081:80 --shm-size=512m ${NEW_IMAGE}"
    echo ""
    echo "删除原容器:"
    echo "  docker stop ${CONTAINER_ID}"
    echo "  docker rm ${CONTAINER_ID}"
}

do_verify() {
    local IMAGE="$1"

    echo -e "${YELLOW}🔍 验证镜像...${NC}"
    echo ""

    if docker image inspect "${IMAGE}" &> /dev/null; then
        echo -e "${GREEN}✅ 镜像存在: ${IMAGE}${NC}"
        echo ""
        docker image inspect "${IMAGE}" --format '
  ID:      {{.ID}}
  创建时间: {{.Created}}
  大小:    {{.Size}} bytes
  作者:    {{.Author}}
  注释:    {{.Comment}}'
    else
        echo -e "${RED}❌ 镜像不存在: ${IMAGE}${NC}"
    fi
}

# ── 主入口 ──
print_banner

case "${1:-help}" in
    list|ls)
        show_containers
        ;;
    commit|save)
        CONTAINER_ID="${2:-}"
        NEW_IMAGE="${3:-}"
        if [ -z "${CONTAINER_ID}" ] || [ -z "${NEW_IMAGE}" ]; then
            echo "用法: $0 commit <容器ID> <新镜像名> [作者] [描述]"
            echo ""
            show_containers
            exit 1
        fi
        do_commit "${CONTAINER_ID}" "${NEW_IMAGE}" "${4:-wangqiuzhuang}" "${5:-}"
        ;;
    verify|check)
        IMAGE="${2:-}"
        if [ -z "${IMAGE}" ]; then
            echo "用法: $0 verify <镜像名>"
            echo ""
            docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}"
            exit 1
        fi
        do_verify "${IMAGE}"
        ;;
    *)
        echo "用法: $0 {list|commit|verify}"
        echo ""
        echo "  list       - 查看运行中的容器"
        echo "  commit     - 保存容器为新镜像"
        echo "  verify     - 验证镜像是否存在"
        echo ""
        echo "示例:"
        echo "  $0 list"
        echo "  $0 commit 9b76cfdb3097 wangqiuzhuang/custom"
        echo "  $0 verify wangqiuzhuang/custom"
        ;;
esac
