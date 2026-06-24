# Week 10: 实验反思

## 1. 本周我学到了什么？

本周重点学了两块内容：Docker 卷挂载和 OpenCV 图像处理入门。

Docker 方面，以前我只知道 `docker run` 启动容器，但不理解数据怎么在宿主机和容器之间流动。`-v` 挂载的本质是 Linux mount namespace 的文件共享，不是"拷贝"，这让我对容器的存储机制有了更清晰的认识。还有一个很实用的细节：PowerShell 退出后容器连接断开的问题。学会了 `-d` 后台模式和 `Ctrl+P Ctrl+Q` 分离终端后，就不再被终端窗口绑住了。

OpenCV 方面，从安装到跑通第一个图像处理 demo，踩了环境配置的坑（多 Python 环境、ROS2 Python 路径冲突），但最终理解了 BGR 和 RGB 的历史差异、几种图像平滑方法的适用场景。这些基础知识虽然简单，但后续做机器人视觉（比如 ArUco 标记检测、目标跟踪）都离不开。

## 2. 遇到了什么困难？怎么解决的？

最大的困难是 Python 环境混乱。Docker 容器里有系统 Python（3.10）、ROS2 自带的 Python 环境、还有 pip 安装的包分散在不同路径。执行 `pip install opencv-python` 后，`import cv2` 仍然报错 ModuleNotFoundError。

解决方案是搞清楚 `which python` 和 `which pip` 分别指向哪里，然后用 `python -m pip install` 确保安装到当前解释器。更深层的理解是：ROS2 的 Python 包应该优先走 `apt install ros-humble-*`，而不是直接 pip，避免和 ROS2 的依赖冲突。

另一个麻烦是 Docker 容器跑起来后需要的磁盘空间比预想的大很多。实验截图、OpenCV 处理结果、ROS2 log 会悄悄占满 Docker 的虚拟磁盘。后来学会了 `docker system prune` 定期清理。

## 3. 这些知识和技能如何与更广泛的机器人概念关联？

本周学到的 Docker 卷挂载和 OpenCV 基础，本质上是搭建了「开发环境」和「感知能力」两个基础。

在机器人开发中，环境的一致性非常重要。一个人用 Mac、另一个人用 Windows，如果没有 Docker，光是配环境就能花掉一半时间。卷挂载让代码修改和容器运行解耦 —— 代码在宿主机上写，运行环境在容器里，互不干扰。

OpenCV 这块更是机器人感知的基础。从简单的图像读取、颜色转换，到后续的特征提取、目标检测、ArUco 标记识别，都是在这些基础 API 上构建的。理解底层（比如 BGR 通道顺序、滤波的数学原理）能让你在遇到奇怪 bug 时快速定位原因，而不是盲目调参数。

如果要进一步提升，我接下来想做的是：把 OpenCV 处理流程接到 ROS2 的 `/camera/image_raw` 话题上，在 Docker 容器里跑一个实时的图像预处理节点，把处理结果通过 RViz2 可视化出来。这样本周的零散知识点就能串联成一个完整的机器人视觉 pipeline。
