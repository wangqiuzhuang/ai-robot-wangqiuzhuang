# Week 10: AI 对话记录

> 以下为本周实验中与 AI 助手的真实对话摘录，共 6 轮。主要围绕 Docker 卷挂载的原理、OpenCV 图像处理及 Python 依赖兼容性问题展开。

---

## 第 1 轮

**我：**
Docker 的 `-v` 参数挂载目录后，本地改了文件容器里真的能实时看到吗？是双向同步还是单向的？

**AI：**
`docker run -v` 默认是双向同步的（bind mount）。你在宿主机上修改文件，容器内立刻能看到；反之亦然。底层原理是 Linux 内核的 mount namespace —— 容器和宿主机共享同一个 inode，不存在"拷贝"，两边读写的其实是同一份数据。

注意区分两种挂载方式：
- **Bind mount** (`-v /host/path:/container/path`)：双向同步，直接映射宿主机目录
- **Volume** (`-v volume_name:/container/path`)：Docker 管理的存储，默认单向

你用的是 bind mount，所以本地 PowerShel 里改了 Python 文件，容器里立刻生效。

---

## 第 2 轮

**我：**
我挂载成功了，但退出 PowerShell 之后连接就断了。有什么办法让容器在后台一直跑着，不依赖 PowerShell 窗口？

**AI：**
加 `-d` 参数就行：`docker run -d -v ...`。这样容器在后台运行为 daemon 模式，不绑定终端。

不过你的场景比较特殊 —— 用的是 `ghcr.io/tiryoh/ros2-desktop-vnc` 镜像，需要在容器内通过 VNC 访问桌面环境。如果只是跑无头脚本，`-d` 完全没问题；但需要 GUI 的话，VNC 端口 (`-p 6081:80`) 不受影响，你依然可以通过浏览器访问 `localhost:6081`。

如果已经在跑的容器不想关掉重来，可以先 `docker ps` 找到容器 ID，然后 Ctrl+P Ctrl+Q 分离终端（不停止容器）。

---

## 第 3 轮

**我：**
OpenCV 读进来的图片为什么是 BGR 而不是 RGB？这个设计有什么特别的理由吗？

**AI：**
这是历史遗留问题。OpenCV 最早在 Intel 的 IPP 库基础上开发，当时 Intel 的硬件处理顺序是 BGR（小端序、与 Windows BITMAP 格式兼容），所以 OpenCV 默认用 BGR 顺序。Matplotlib 用 RGB 显示，所以经常需要 `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)` 转一下。

不过 OpenCV 的 `imwrite` 写文件会自动处理通道顺序，所以保存出来的图片用其他软件打开不会有颜色问题。只有直接在代码里用 matplotlib 显示时才需要注意。

---

## 第 4 轮

**我：**
跑 OpenCV 教程代码时报了 `ModuleNotFoundError: No module named 'cv2'`，但我明明 pip install 了。怎么回事？

**AI：**
大概率是多个 Python 环境的问题。Docker 容器里可能同时装了系统 Python 和 conda，你 pip install 到了一个环境，但实际运行用的是另一个。

排查步骤：
1. `which python` 和 `which pip` 看是不是同一个路径
2. `python -c "import sys; print(sys.path)"` 检查搜索路径
3. 如果是 conda 和系统 Python 混用，统一用 `python -m pip install opencv-python` 确保装到当前解释器

你的容器里还有 ROS2 的 Python 环境（`/opt/ros/humble/lib/python3.10/`），更复杂。建议用 `pip install --target` 指定安装位置，或者直接 `apt install ros-humble-cv-bridge` 走 ROS2 包管理。

---

## 第 5 轮

**我：**
我看到 OpenCV 有好几种图像平滑方法 —— 高斯模糊、中值滤波、双边滤波，到底什么时候该用哪种？能不能举个机器人的实际例子？

**AI：**
区别核心在于"要不要保留边缘"：

| 方法 | 原理 | 边缘保留 | 机器人场景 |
|------|------|:---:|------|
| 高斯模糊 | 加权平均，权重按距离衰减 | ❌ 边缘一起糊 | 预处理降噪（ArUco 标记检测前） |
| 中值滤波 | 取邻域中值 | ⚠️ 部分保留 | 去除椒盐噪声（LiDAR 点云异常点） |
| 双边滤波 | 空间+颜色双重加权 | ✅ 保留边缘 | 需要保留物体轮廓的场景（障碍物检测） |

举个例子：你在做 ArUco 标记检测时，标记边缘必须清晰，所以用高斯模糊（小核 + 低 sigma）就够了，不能用双边滤波把标记边框给吃掉。反过来，如果是做物体分割要保留轮廓，双边滤波更合适。

---

## 第 6 轮

**我：**
总结一下本周我学了什么？如果要把这周的 Docker + OpenCV 技能用到机器人项目上，能做什么？

**AI：**
本周你掌握了两个关键能力：

1. **Docker 卷挂载**：宿主机写代码 → 容器里跑 ROS2/OpenCV，不用每次 rebuild 镜像。这在机器人开发里非常实用，因为仿真环境（Gazebo/Webots）的启动很慢，你不会想为了改一行代码就重建镜像。

2. **OpenCV 图像处理基础**：图像的读取、颜色空间转换、平滑滤波。这是机器人视觉的入门砖。

结合起来的典型场景：在宿主机上写 OpenCV 图像预处理脚本，通过 Docker 卷挂载同步到容器，在容器里调用 ROS2 的图像话题（`/camera/image_raw`）进行实时处理，处理结果通过 VNC 查看。这就是一个最小化的机器人视觉开发工作流。
