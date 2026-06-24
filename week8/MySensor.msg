# Week 8: 自定义 ROS2 消息接口定义
# ===================================
# 实验用自定义传感器消息: 包含传感器 ID、名称、读数和校准状态
#
# 编译方式:
#   将本文件放在 ROS2 包的 msg/ 目录下
#   在 CMakeLists.txt 和 package.xml 中配置 rosidl 接口生成
#   colcon build 后使用:
#     ros2 interface show my_package/msg/MySensor

# 标准消息头 (时间戳 + frame_id)
std_msgs/Header header

# 传感器标识
int32 sensor_id
string sensor_name

# 传感器读数 (可变长度浮点数组)
float64[] readings

# 校准状态
bool is_calibrated

# 传感器类型枚举 (0=未知, 1=LiDAR, 2=相机, 3=IMU, 4=超声波)
int32 sensor_type
