# Week 1: 基础环境搭建与工程工具

## 本周概览

- WSL2 安装与配置
- Ubuntu 22.04 LTS 环境初始化
- Git 版本控制基础与 GitHub 工作流
- Markdown 文档编写规范
- GitHub 仓库创建与 Pages 部署

---

## 1. WSL2 安装与原理

### 什么是 WSL2？

WSL2（Windows Subsystem for Linux 2）是 Microsoft 开发的 Linux 兼容层，它在一个轻量级虚拟机中运行完整的 Linux 内核。相比 WSL1 的系统调用翻译层，WSL2 提供：
- **完整的 Linux 内核**：支持所有 Linux 系统调用
- **接近原生的 I/O 性能**：文件系统操作速度大幅提升
- **Docker 原生支持**：可直接运行 Docker 守护进程
- **GPU 加速**：支持 CUDA 等 GPU 计算

### 安装步骤

在 **Windows PowerShell (管理员)** 中执行：

```bash
wsl --install
```

该命令会自动完成以下安装：
1. 启用「Windows 虚拟机监控程序平台」
2. 启用「适用于 Linux 的 Windows 子系统」
3. 下载并安装 Ubuntu 22.04 LTS
4. 将 Ubuntu 设为默认发行版

安装完成后 **重启电脑**，首次启动 Ubuntu 时设置用户名和密码。

> ⚠️ **注意**：如果安装失败，检查 BIOS 中是否开启了虚拟化技术（Intel VT-x / AMD-V）。

---

## 2. Ubuntu 环境初始化

```bash
# 更新软件包索引并升级已安装的包
sudo apt update && sudo apt upgrade -y

# 安装基础开发工具链
sudo apt install -y build-essential curl wget git vim

# 验证安装
gcc --version    # C 编译器
git --version    # Git 版本控制
python3 --version # Python 解释器
```

### 更换国内镜像源（加速下载）

```bash
# 备份原始源
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak

# 替换为清华镜像源
sudo sed -i 's/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list
sudo apt update
```

---

## 3. Git 配置与 GitHub SSH 密钥

### 3.1 用户信息配置

```bash
git config --global user.name "wangqiuzhuang"
git config --global user.email "your-email@example.com"

# 查看配置
git config --list
```

### 3.2 SSH 密钥生成与添加

SSH 密钥用于安全、免密地与 GitHub 通信：

```bash
# 生成 ED25519 密钥（推荐，比 RSA 更安全更快）
ssh-keygen -t ed25519 -C "your-email@example.com"
# 一路回车使用默认路径 ~/.ssh/id_ed25519

# 启动 ssh-agent 并添加密钥
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 查看公钥内容，复制到 GitHub → Settings → SSH and GPG keys
cat ~/.ssh/id_ed25519.pub
```

> 💡 **原理**：SSH 使用非对称加密。私钥 (`id_ed25519`) 保存在本地，公钥 (`.pub`) 上传到 GitHub。连接时 GitHub 用公钥加密挑战，只有持有私钥的你能解密回应，从而验证身份。

### 3.3 Git 基本工作流

```bash
git init                      # 初始化本地仓库
git add .                     # 暂存所有更改到索引
git commit -m "描述信息"       # 提交到本地仓库
git push origin main          # 推送到远程 (GitHub)
git pull origin main          # 拉取远程更新
git status                    # 查看工作区状态
git log --oneline             # 查看提交历史
```

---

## 4. Markdown 文档规范

作为课程实验记录的标准格式，Markdown 需掌握：

```markdown
# 一级标题（每篇文档仅一个）
## 二级标题（主要章节）
### 三级标题（子章节）

**粗体强调** *斜体*
`行内代码`

- 无序列表项 1
- 无序列表项 2

1. 有序列表项 1
2. 有序列表项 2

代码块（指定语言以启用语法高亮）：
```python
print("Hello, AI Robot!")
```

图片（使用相对路径，避免外部链接）：
![图片描述](img/screenshot.png)

链接：
[GitHub](https://github.com)

表格：
| 列1 | 列2 | 列3 |
|:---|:---|:---|
| A | B | C |
```

---

## 5. GitHub 仓库与 Pages 部署

### 创建课程仓库

1. 在 GitHub 点击 **New Repository**
2. 命名为 `ai-robot-wangqiuzhuang`
3. 设置为 **Public**（课程系统需要公开访问）
4. 勾选 "Add a README file"
5. 点击 **Create repository**

### 启用 GitHub Pages

1. 进入仓库 **Settings → Pages**
2. **Source** 选择 `main` 分支，根目录 `/ (root)`
3. 点击 **Save**
4. 等待 1-2 分钟，访问 `https://wangqiuzhuang.github.io/ai-robot-wangqiuzhuang/`

---

## 踩坑记录

| 问题 | 原因 | 解决方案 |
|:---|:---|:---|
| `wsl --install` 报错 | BIOS 虚拟化未开启 | 重启进入 BIOS，开启 Intel VT-x / AMD-V |
| `wsl: 系统找不到指定的文件` | Windows 功能未启用 | 控制面板 → 启用「虚拟机平台」和「Linux 子系统」 |
| `git push` 要求密码 | 使用了 HTTPS 而非 SSH | `git remote set-url origin git@github.com:user/repo.git` |
| SSH 连接 Permission denied | 公钥未添加到 GitHub | Settings → SSH Keys → New SSH Key → 粘贴公钥 |

---

## 总结

本周完成了 AI 机器人课程的基础开发环境搭建。核心收获：

1. **WSL2 原理**：理解其作为轻量级虚拟机运行完整 Linux 内核的架构
2. **Git 工作流**：掌握 init → add → commit → push 的标准版本控制流程
3. **SSH 认证**：理解非对称加密在 Git 免密通信中的应用
4. **Markdown 规范**：为后续所有实验记录建立了统一的文档格式
5. **GitHub Pages**：完成了课程作业展示网站的基础部署

以上基础为后续 ROS2 开发、Docker 容器化和机器人仿真实验做好了准备。
