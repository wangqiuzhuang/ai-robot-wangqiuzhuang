# Week 11: 实验反思

## 1. 本周我学到了什么？

本周完成了两个看似独立但实则互补的任务：Docker 镜像持久化和 Git 仓库整理。

Docker 方面，`docker commit` 解决了大问题 —— 之前每次容器关掉所有操作都丢失，现在可以把配好的环境保存为镜像，下次直接跑。这个流程在机器人开发里特别有用：装好的 ROS2 包、编译好的工作空间、配置好的网络环境，commit 成镜像后不用担心重装。

Git 方面，最大的教训是 submodule 和 GitHub Pages 的兼容性问题。一开始把 week13 做成 submodule，结果 GitHub Pages 直接 404。排查了半天才明白是 Jekyll 构建不支持 submodule。最后反思：课程作业场景下，submodule 带来的"上游跟踪"优势远不如"简单直接"重要。**选择技术方案要看实际场景，不是越高级越好。**

## 2. 遇到了什么困难？怎么解决的？

最大的坑是 GitHub Pages 部署的图片碎链。在本地 VS Code 预览完全正常，push 上去就全是 404。排查发现是相对路径的问题 —— Jekyll 的 `baseurl` 和 `relative_url` 过滤器必须正确配置 `_config.yml` 才能工作。我的问题出在：图片引用用了 `![img](week11/img/xxx.png)` 而没有加 `/ai-robot-wangqiuzhuang/` 前缀。

解决方式有两个方向：一是在 `_config.yml` 里正确设置 `baseurl`，然后所有链接用 `site.baseurl` 变量前缀；二是直接用相对于仓库根的路径。我选了第二种，因为更简单直接，不依赖 Jekyll 变量。

另一个坑是 `docker commit` 后镜像体积暴增。查了一下发现是容器里 `apt update` 的缓存和 ROS2 log 没有清理。养成习惯：commit 前 `apt clean && rm -rf /var/lib/apt/lists/* && rosclean purge`。

## 3. 这些知识和技能如何与更广泛的机器人概念关联？

Docker 在机器人领域越来越重要。ROS2 官方本身就推荐用 Docker 做开发环境隔离。实际机器人项目中，Docker 的优点：
- 仿真环境一致（Gazebo/Ignition 版本不会因为系统升级而挂掉）
- 多机器人协同（每个机器人跑在独立容器里，通过 ROS2 DDS 通信）
- CI/CD 自动化测试（每次 push 自动在容器里跑仿真测试）

Git 仓库管理则是工程素养的体现。一个好的机器人项目通常包含：文档、源码、仿真配置、硬件驱动、测试用例。没有清晰的目录结构和版本管理，根本维护不下去。本周学的 GitHub Pages 部署，本质上是把技术文档"发布"出去 —— 写得好别人看得懂，协作才有效率。

接下来最感兴趣的方向是：把 Docker 容器 + ROS2 仿真 + GitHub Actions CI 串起来，实现"push 代码 → 自动跑 Gazebo 仿真测试 → 测试结果回传 Issue"，这个 pipeline 在真实的机器人公司是标配。
