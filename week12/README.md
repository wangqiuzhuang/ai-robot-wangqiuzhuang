# Week 12: 远程摄像头流与 ArUco 标记识别 ⭐

> 🎯 **冲A+核心周** — 本周实验打通了手机摄像头 → WSL → OpenCV 的完整数据链路

## 本周概览

- Tailscale 跨设备组网（WSL ↔ 手机）
- Termius SSH 远程终端连接
- 手机浏览器摄像头流实时传输到 Python/OpenCV
- ArUco 标记生成与实时识别

---

## 操作步骤

### 1. 课件地址

[https://course.a-real.me/content/week12.html](https://course.a-real.me/content/week12.html)

### 2. WSL 安装 Tailscale

在 WSL 中执行 Tailscale 安装指令，使用 Google 账号登录完成设备注册：

![WSL安装Tailscale](img/wsl安装Tailscale.png)

### 3. 手机端安装 Tailscale

手机应用商店下载 Tailscale，使用与步骤 2 相同的 Google 账号登录。

### 4. 手机 SSH 远程连接 WSL

手机下载终端工具 **Termius**，使用 WSL 的用户名和密码远程连接：

![手机远程连接WSL成功](img/手机远程连接wsl成功截图.jpg)

### 5. 验证设备互联

连接成功后，PC 端 Tailscale 控制台可以看到全部在线设备：

![PC端控制台截图](img/PC端控制台截图.png)

### 6. 安装 SSH 服务

在 WSL 中执行以下指令安装并启动 SSH 服务：

![安装SSH服务](img/安装ssh服务指令.png)

### 7. 克隆实验代码

```bash
git clone https://github.com/ai-robot-class/ai-robot-class.github.io.git
```

### 8. 安装 Python 依赖

![安装pip3](img/安装pip3指令截图.png)

进入项目目录，安装依赖：

```bash
cd ai-robot-class.github.io
pip install -r week12_starters/requirements.txt
```

![执行Python脚本](img/调用摄像头py程序执行截图.png)

### 9. 手机浏览器访问摄像头页面

在手机浏览器中访问 `http://<wsl-ip>:5000`（IP 地址和端口以实际为准），页面会发起摄像头权限请求：

![手机浏览器调用摄像头成功](img/手机浏览器调用摄像头成功截图.jpg)

![Python解码成功](img/python代码处理手机摄像过上传图片病解析成功截图.jpg)

### 10. 验证视频流稳定性

手机画面能够稳定出现在 WSL 的 OpenCV 窗口中，实时视频流传输成功。

### 11. 代码架构解析

```
手机浏览器 (HTTPS 页面)
    │ 调用摄像头
    │ JPEG 帧 → WebSocket
    ▼
WSL Python 服务端
    │ OpenCV 解码
    │ 实时显示
    ▼
OpenCV 显示窗口
```

核心流程：WSL 托管 HTTPS 页面 → 手机浏览器打开页面 → 页面调用摄像头 → JPEG 帧通过 WebSocket 发送到 Python → OpenCV 解码并显示

### 12. ArUco 标记生成与识别

访问 [ArUco Marker Generator](https://chev.me/arucogen/) 在线生成 ArUco 标记：

![ArUco标记生成器](img/ArUcomarkersgenerator.png)

### 13. 刷新验证

刷新浏览器，重新获取摄像头权限，触发摄像头重新取样关键帧：

![最终解析结果](img/最终解析出来的图片截图.jpg)

### 14. 验证结果

解析得到的 ArUco 数据与输入的图像数据一致，任务完成！✅

---

## 踩坑记录

| 问题 | 原因 | 解决方案 |
|:---|:---|:---|
| 浏览器刷新一直超时 | WSL 中运行的程序端口挂起 | 杀死 WSL 中运行的程序，重新 `run` 后浏览器刷新秒入 |

---

## 总结

本周是课程中的 **冲A+核心实验**，成功搭建了跨设备的实时摄像头流传输链路，打通了「手机摄像头 → Tailscale 组网 → WSL Python/OpenCV → ArUco 识别」的完整数据管道。这一架构可扩展至远程机器人视觉、移动端 AI 推理等实际应用场景。

## 代码说明

**`aruco_detect.py`** — ArUco 标记实时检测器
- 支持 4×4 / 5×5 / 6×6 / 7×7 四种 ArUco 字典
- 实时摄像头检测模式：逐帧检测标记并绘制边框和 ID
- 单图检测模式：检测图片中的标记并保存标注结果
- 按 's' 截图保存，按 'q' 退出

**`camera_server.py`** — 手机摄像头 WebSocket 服务器
- Flask + SocketIO 实现手机浏览器到 WSL 的图像流传输
- HTML5 getUserMedia 调用手机摄像头
- Base64 JPEG 编码传输，服务器端 OpenCV 解码
- 预留 ArUco 检测接口

## 运行方式

```bash
pip install opencv-contrib-python flask flask-socketio
cd week12

# ArUco 实时检测 (需要摄像头)
python3 aruco_detect.py

# 或检测单张图片
python3 aruco_detect.py --image test.jpg

# 手机摄像头服务器 (手机浏览器访问 http://<wsl-ip>:5000)
python3 camera_server.py
```
