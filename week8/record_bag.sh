#!/bin/bash
# Week 8: ROS2 Bag 录制与回放脚本
# =================================
# 一键录制小乌龟实验数据，支持回放和倍速控制。
#
# 使用方式:
#   录制: ./record_bag.sh record
#   回放: ./record_bag.sh play
#   信息: ./record_bag.sh info
#   回放(2x): ./record_bag.sh play2x

set -e

BAG_NAME="turtlesim_experiment"
TOPICS="/turtle1/pose /turtle1/cmd_vel"
ROS_DISTRO="${ROS_DISTRO:-humble}"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_banner() {
    echo -e "${GREEN}=================================${NC}"
    echo -e "${GREEN}  ROS2 Bag 数据录制工具${NC}"
    echo -e "${GREEN}=================================${NC}"
    echo ""
}

check_ros2() {
    if ! command -v ros2 &> /dev/null; then
        echo -e "${RED}❌ ros2 未找到！请先 source ROS2 环境。${NC}"
        echo "   source /opt/ros/${ROS_DISTRO}/setup.bash"
        exit 1
    fi
}

cmd_record() {
    echo -e "${YELLOW}🔴 开始录制...${NC}"
    echo "   话题: ${TOPICS}"
    echo "   输出: ${BAG_NAME}"
    echo ""
    echo "   💡 提示: 在另一个终端操作小乌龟，数据将被录制"
    echo "   按 Ctrl+C 停止录制"
    echo ""

    ros2 bag record -o "${BAG_NAME}" ${TOPICS}
}

cmd_play() {
    if [ ! -d "${BAG_NAME}" ]; then
        echo -e "${RED}❌ Bag 文件不存在: ${BAG_NAME}${NC}"
        echo "   请先执行: $0 record"
        exit 1
    fi

    echo -e "${GREEN}▶️  开始回放...${NC}"
    ros2 bag play "${BAG_NAME}"
}

cmd_play_2x() {
    if [ ! -d "${BAG_NAME}" ]; then
        echo -e "${RED}❌ Bag 文件不存在: ${BAG_NAME}${NC}"
        exit 1
    fi

    echo -e "${GREEN}▶️  2x 倍速回放...${NC}"
    ros2 bag play "${BAG_NAME}" --rate 2.0
}

cmd_info() {
    if [ ! -d "${BAG_NAME}" ]; then
        echo -e "${RED}❌ Bag 文件不存在: ${BAG_NAME}${NC}"
        exit 1
    fi

    echo -e "${GREEN}📋 Bag 文件信息:${NC}"
    echo ""
    ros2 bag info "${BAG_NAME}"
}

# ── 主入口 ──
print_banner
check_ros2

case "${1:-info}" in
    record)
        cmd_record
        ;;
    play)
        cmd_play
        ;;
    play2x)
        cmd_play_2x
        ;;
    info)
        cmd_info
        ;;
    *)
        echo "用法: $0 {record|play|play2x|info}"
        echo ""
        echo "  record  - 录制小乌龟实验数据"
        echo "  play    - 回放录制数据"
        echo "  play2x  - 2倍速回放"
        echo "  info    - 查看 Bag 信息"
        exit 1
        ;;
esac
