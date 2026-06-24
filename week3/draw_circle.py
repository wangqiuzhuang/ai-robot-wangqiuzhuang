#!/usr/bin/env python3
"""
Week 3: 小乌龟画圆控制器
=========================
通过周期性发布速度指令，控制小乌龟在 turtlesim 中画出圆形轨迹。

原理:
  圆周运动 = 恒定线速度 + 恒定角速度
  线速度 v 和角速度 ω 的关系: v = ω × r
  当两者都恒定且非零时，小乌龟做匀速圆周运动

运行方式:
  终端1: ros2 run turtlesim turtlesim_node
  终端2: python3 draw_circle.py
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math


class CircleDrawer(Node):
    """
    画圆控制器

    参数配置:
      - linear_velocity:  线速度 (前进速度)
      - angular_velocity: 角速度 (旋转速度)
      - circle_radius:    期望的圆半径 (计算用，实际取决于 v 和 ω 的比值)

    数学关系:
      r = v / ω  (当 v > 0 且 ω > 0 时)
      周期 T = 2π / ω  (画一圈需要的时间)
    """

    def __init__(self):
        super().__init__('circle_drawer')

        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # 控制参数: 线速度和角速度
        self.linear_vel = 1.5   # m/s
        self.angular_vel = 1.0  # rad/s

        # 计算理论参数
        radius = self.linear_vel / self.angular_vel
        period = 2 * math.pi / self.angular_vel

        self.get_logger().info(f'⭕ 画圆控制器启动: r={radius:.2f}m, T={period:.2f}s')

        # 每 0.1 秒发布一次速度指令
        self.timer = self.create_timer(0.1, self.draw_circle)

    def draw_circle(self):
        """发布恒定的速度指令以实现圆周运动"""
        msg = Twist()
        msg.linear.x = self.linear_vel
        msg.linear.y = 0.0
        msg.angular.z = self.angular_vel
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    drawer = CircleDrawer()

    try:
        rclpy.spin(drawer)
    except KeyboardInterrupt:
        drawer.get_logger().info('🛑 画圆已停止')
    finally:
        drawer.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
