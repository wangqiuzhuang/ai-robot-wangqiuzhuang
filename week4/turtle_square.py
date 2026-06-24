#!/usr/bin/env python3
"""
Week 4: 小乌龟正方形轨迹控制器
===============================
控制 turtlesim 小乌龟走出正方形轨迹。

运动序列 (4条边，每条边 2 秒):
  1. 前进 (东) 2s
  2. 90° 左转
  3. 前进 (北) 2s
  4. 90° 左转
  5. 前进 (西) 2s
  6. 90° 左转
  7. 前进 (南) 2s
  8. 90° 左转 (归位)

实现方式:
  - 使用状态机管理 4 条边 + 4 次转弯
  - 状态 0/2/4/6: 前进
  - 状态 1/3/5/7: 原地旋转 90°

运行方式:
  ros2 run turtlesim turtlesim_node
  python3 turtle_square.py
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math


class SquareDrawer(Node):
    """正方形轨迹控制器 — 状态机实现"""

    # 状态定义
    FORWARD = 0
    TURN = 1

    def __init__(self):
        super().__init__('square_drawer')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # 正方形参数
        self.side_length = 2.0       # 边长 (m)
        self.linear_speed = 1.0      # 前进速度 (m/s)
        self.angular_speed = math.pi / 2  # 旋转速度 (rad/s) → 90° 需要 1s

        self.phase = 0               # 当前阶段 (0-7, 共8个阶段)
        self.phase_start_time = self.get_clock().now()
        self.get_logger().info('🟦 正方形轨迹控制器启动')

        # 每 0.1s 更新
        self.timer = self.create_timer(0.1, self.control_loop)

    def control_loop(self):
        now = self.get_clock().now()
        elapsed = (now - self.phase_start_time).nanoseconds / 1e9  # 转为秒
        msg = Twist()

        side_duration = self.side_length / self.linear_speed   # 走一条边的时间
        turn_duration = (math.pi / 2) / self.angular_speed     # 转 90° 的时间

        if self.phase % 2 == 0:
            # ── 前进阶段 ──
            if elapsed < side_duration:
                msg.linear.x = self.linear_speed
                msg.angular.z = 0.0
            else:
                self.get_logger().info(f'✅ 边 {self.phase // 2 + 1}/4 完成')
                self.phase += 1
                self.phase_start_time = now

        else:
            # ── 转弯阶段 ──
            if elapsed < turn_duration:
                msg.linear.x = 0.0
                msg.angular.z = self.angular_speed
            else:
                self.get_logger().info(f'↩️  转弯 {self.phase // 2 + 1}/4 完成')
                self.phase += 1
                self.phase_start_time = now

        # 画完正方形后停止
        if self.phase >= 8:
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.get_logger().info('🏁 正方形完成! 小乌龟停止。')
            self.timer.cancel()

        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    drawer = SquareDrawer()
    try:
        rclpy.spin(drawer)
    except KeyboardInterrupt:
        drawer.get_logger().info('🛑 已停止')
    finally:
        drawer.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
