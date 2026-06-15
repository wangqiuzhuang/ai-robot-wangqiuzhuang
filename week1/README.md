# Week 1: 基础环境搭建与工程工具

## 本周概览

- WSL2 安装与配置
- Ubuntu 22.04 LTS 环境初始化
- Git 版本控制基础
- Markdown 文档编写规范
- GitHub 仓库创建与管理

## 1. WSL2 安装

在 Windows PowerShell (管理员) 中执行：

```bash
wsl --install
```

该命令会自动安装：
- Windows 虚拟机监控程序平台
- 适用于 Linux 的 Windows 子系统
- Ubuntu 22.04 LTS 发行版

安装完成后重启电脑，首次启动 Ubuntu 时设置用户名和密码。

## 2. Ubuntu 环境初始化

```bash
# 更新软件包列表
sudo apt update && sudo apt upgrade -y

# 安装基础开发工具
sudo apt install -y build-essential curl wget git vim
```

## 3. Git 配置与 GitHub

```bash
# 配置用户信息
git config --global user.name "wangqiuzhuang"
git config --global user.email "your-email@example.com"

# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your-email@example.com"

# 查看公钥（添加到 GitHub Settings → SSH Keys）
cat ~/.ssh/id_ed25519.pub
```

### Git 基本工作流

```bash
git init                    # 初始化仓库
git add .                   # 暂存所有更改
git commit -m "描述信息"      # 提交更改
git push origin main        # 推送到远程仓库
```

## 4. Markdown 基础语法

```markdown
# 一级标题
## 二级标题
### 三级标题

**粗体** *斜体*
- 无序列表
1. 有序列表

`行内代码`
​```python
# 代码块
print("Hello World")
​```

![图片描述](img/example.png)
[链接文字](https://example.com)
```

## 5. 创建课程仓库

1. 在 GitHub 新建仓库 `ai-robot-wangqiuzhuang`
2. 设置为 **Public**（公开）
3. 启用 GitHub Pages（Settings → Pages → Source: main branch）
4. 本地克隆并开始每周作业提交

## 总结

本周完成了 AI 机器人课程的基础开发环境搭建，包括 WSL2 + Ubuntu 子系统、Git 版本控制工具链以及 Markdown 文档编写规范的熟悉，为后续 ROS2 开发和机器人仿真实验打下基础。
