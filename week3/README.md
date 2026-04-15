# wangqiuzhuang's third week's homework description  
## git  
1. 设置github ssh密钥并进行ubuntu里的命令行交互
2. git常用指令练习  略
3. git常用指令练习  略
4. 初始化git配置  第一次推荐用ssh方式  后续可以使用http方式

## vs code 与wsl ubuntu交互  
1. 下载安装vscode
2. 配置wsl工具
3. 连接到wsl目录
2. 设置vs code 与wsl ubuntu交互
3. 运行小乌龟节点，进行ros命令行交互

## homework and desc  
- 运行小乌龟节点，进行ros命令行交互
- 先开一个ubuntu teminal命令行窗口  ros2 run turtlesim turtlesim_node  
- 另开一个窗口运行   ros2 topic echo /turtle1/pose  
- 另开一个窗口运行 ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
  小乌龟位置监听截图：
<img width="1255" height="711" alt="image" src="https://github.com/user-attachments/assets/d5896b3a-fb93-47b0-9d25-83c06e4574cc" />
小乌龟移动控制截图：
<img width="1234" height="1225" alt="image" src="https://github.com/user-attachments/assets/162e08dd-7304-4bf6-8419-e6288ef8a2a8" />
