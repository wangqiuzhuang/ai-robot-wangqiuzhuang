# Week 11: AI 对话记录

> 以下为本周实验中与 AI 助手的真实对话摘录，共 5 轮。主要围绕 Docker 镜像持久化、Git 仓库整理及 GitHub Pages 部署。

---

## 第 1 轮

**我：**
docker commit 到底干了什么？它和 Dockerfile + docker build 有什么区别？我什么时候该用 commit 而不是写 Dockerfile？

**AI：**
`docker commit` 是把当前容器的文件系统快照保存为一个新的镜像层。本质上是 `docker export` + `docker import` 的简化版。

和 Dockerfile 的核心区别：

| | docker commit | Dockerfile |
|---|---|---|
| 可复现性 | ❌ 手动操作无法复现 | ✅ `docker build` 随时重来 |
| 版本管理 | ❌ 不知道改了什么 | ✅ 每一行变更都有记录 |
| 速度 | 快（改完立刻保存） | 慢（需要从头 build） |
| 适用场景 | 实验调试、临时保存状态 | 生产部署、团队协作 |

你的场景（课程实验）其实特别适合 commit：在容器里装了一堆依赖、改了很多配置，最后 `docker commit` 保存状态，下次直接 `docker run` 新镜像继续干活。但如果是正式项目，还是老老实实写 Dockerfile。

---

## 第 2 轮

**我：**
我用 docker commit 保存了镜像，但镜像名字和 TAG 怎么管理？每次都叫 v1、v2、v3 感觉有点混乱。

**AI：**
推荐的命名规范：`<name>:<date>-<description>`，比如：
```
my-ros2-humble:20250321-opencv
my-ros2-humble:20250322-added-ssh
```

或者加个 `latest` 标签指向你最常用的版本：
```bash
docker tag my-ros2-humble:20250322-added-ssh my-ros2-humble:latest
```

每次 commit 完立刻打 tag，不要等到想用的时候才翻 `docker images` 找 ID。
也可以用 `docker image ls --filter "reference=my-ros2*"` 按名称过滤。

---

## 第 3 轮

**我：**
我的作业仓库本来是按周次分目录的，但有几个周用了 git submodule（比如 week13），导致 GitHub Pages 部署时 404。submodule 和直接放代码到底选哪个？

**AI：**
GitHub Pages 对 submodule 的支持取决于你用的构建方式：

- **默认 Jekyll 构建**：不支持 submodule 内容渲染，会 404
- **GitHub Actions 自定义构建**：可以在 workflow 里 `git submodule update --init --recursive`，能正常渲染

你当前用的是默认 Jekyll，所以 submodule 里的 README.md 不会被转换。有两个方案：

**方案 A（简单粗暴）**：去掉 submodule，直接把代码拷进 `week13/` 目录。缺点是无法跟踪上游更新。

**方案 B（保留 submodule + 改 CI）**：写一个 `.github/workflows/pages.yml`，用 GitHub Actions 来构建，在构建步骤里初始化 submodule。这样既保留了上游跟踪能力，又能正常渲染。

对你来说，课程作业没必要保留 submodule（上游代码也不会频繁更新），方案 A 更合适。我之前也这么处理过。

---

## 第 4 轮

**我：**
README.md 里能不能放视频？我看有的 GitHub 仓库 README 有动图效果很好，是怎么做的？

**AI：**
GitHub 的 Markdown 不支持直接嵌入视频（`<video>` 标签会被过滤），但有几个替代方案：

1. **GIF 动图**（最推荐）：`![demo](img/demo.gif)`，简单直接，GitHub 原生支持。用 ScreenToGif 或 OBS 录屏转 GIF。

2. **YouTube / Bilibili 外链**：`[![demo](thumbnail.png)](https://youtu.be/xxx)`，点图片跳转视频。

3. **asciinema**：如果是终端操作演示，录成 asciinema 然后嵌入 Markdown。

对于你的实验笔记，建议关键操作过程录成 GIF（10-15 秒，控制文件大小在 5MB 以内），放 `img/` 目录下，README 里直接引用。GitHub Pages 也支持。

---

## 第 5 轮

**我：**
最后帮我总结一下，如果我的作业仓库要给教授看（用来申请研究生），哪些地方应该重点打磨？

**AI：**
如果作业仓库要用来申请研究生（特别是 AI/机器人方向），教授会关注这几个点：

1. **README 是你的门面**：第一屏要说清楚你是谁、做了什么、用了什么技术。加一张仓库结构图（ASCII art 就行）让人 30 秒看懂全貌。

2. **不要只有操作步骤截图**：加"做了什么决策、为什么这样做、踩了什么坑"。教授想看的是你的思考过程，不是你的操作手册。

3. **代码注释**：关键函数的 docstring 和模块说明要有。不用每行都写，但核心逻辑和设计决策要看得出来。

4. **量化成果**：比如"13周实验、18个 Python 脚本、80+ 截图、约 3500+ 行代码"——这些数字让教授快速评估你的工程规模。

5. **目录规范**：每个 week 有独立的 README + img/ + 代码文件，不要把所有东西丢在根目录。这和写论文要有清晰的章节结构是一个道理。

你的仓库已经有不错的骨架了，需要补的主要是 2 和 4。
