#!/usr/bin/env python3
"""
Week 3: 小乌龟螺旋线控制器
===========================
通过逐渐增大线速度或角速度，让 turtlesim 小乌龟画出螺旋线。

变体:
  - 阿基米德螺旋: 线速度恒定，角速度逐渐减小 → 半径逐渐增大
  - 对数螺旋:    角速度恒定，线速度逐渐增大 → 半径呈指数增长

运行方式:
  ros2 run turtlesim turtlesim_node
  python3 turtle_spiral.py
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math


class SpiralDrawer(Node):
    """螺旋线控制器 — 逐渐变化的圆周运动"""

    def __init__(self):
        super().__init__('spiral_drawer')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.step = 0
        self.get_logger().info('🌀 螺旋线控制器启动 (阿基米德螺旋)')

        # 每 0.2 秒更新一次
        self.timer = self.create_timer(0.2, self.draw_spiral)

    def draw_spiral(self):
        """阿基米德螺旋: v 恒定，ω 逐渐减小 → r = v/ω 逐渐增大"""
        self.step += 1

        msg = Twist()
        msg.linear.x = 1.0  # 恒定线速度

        # 角速度从 1.5 逐渐降到 0.3 (半径逐渐增大)
        decay_factor = max(0.3, 1.5 - self.step * 0.005)
        msg.angular.z = decay_factor

        if self.step % 25 == 0:
            current_radius = msg.linear.x / msg.angular.z
            self.get_logger().info(
                f'🌀 第 {self.step} 步: ω={decay_factor:.3f}, r≈{current_radius:.2f}m'
            )

        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    drawer = SpiralDrawer()
    try:
        rclpy.spin(drawer)
    except KeyboardInterrupt:
        drawer.get_logger().info('🛑 螺旋绘制已停止')
    finally:
        drawer.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
