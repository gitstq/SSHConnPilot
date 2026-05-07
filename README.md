<div align="center">

# 🔐 SSHConnPilot

**Lightweight AI-Powered SSH Connection Intelligence Manager CLI**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)](https://github.com/gitstq/SSHConnPilot)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen)](requirements.txt)

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>
## 🇺🇸 English

### 🎉 Project Introduction

**SSHConnPilot** is a lightweight, zero-dependency Python CLI tool designed for developers and system administrators who manage multiple SSH connections daily. It combines AI-assisted configuration suggestions, secure credential storage, connection analytics, and an intuitive interface to streamline your SSH workflow.

**Key Differentiators:**
- 🤖 **AI-Assisted Configuration**: Smart suggestions based on server descriptions
- 🔐 **Secure Credential Storage**: Local encryption for sensitive data
- 📊 **Connection Analytics**: Track usage patterns and statistics
- 🎯 **Zero Dependencies**: Pure Python standard library
- 🌈 **Beautiful Terminal UI**: Colorful, intuitive interface

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Suggestions** | Generate configuration templates from natural language descriptions |
| 🔐 **Secure Storage** | AES-like encryption for credentials, 700 permissions for config files |
| 📊 **Analytics** | Connection history, usage statistics, top hosts |
| 🏷️ **Tag System** | Organize hosts with custom tags and filters |
| 🔄 **Import/Export** | Support JSON and OpenSSH config formats |
| 🧪 **Connection Testing** | Test SSH connectivity without full login |
| 💻 **Interactive Mode** | Shell-like interactive interface for daily use |
| 🚀 **Quick Connect** | One-off connections without saving to database |

### 🚀 Quick Start

#### Requirements
- Python 3.8 or higher
- SSH client installed

#### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/SSHConnPilot.git
cd SSHConnPilot

# Install (optional)
pip install -e .

# Or run directly
python3 sshconnpilot.py
```

#### Basic Usage

```bash
# Launch interactive mode
python3 sshconnpilot.py

# Add a new host
python3 sshconnpilot.py add -n web-server --host 192.168.1.10 -u ubuntu -t "production,web"

# List all hosts
python3 sshconnpilot.py list

# Connect to a host
python3 sshconnpilot.py connect web-server

# Get AI configuration suggestions
python3 sshconnpilot.py suggest "AWS EC2 Ubuntu production server"

# Quick connect without saving
python3 sshconnpilot.py quick --host server.com -u root
```

### 📖 Detailed Usage Guide

#### Adding Hosts

```bash
# Basic usage
python3 sshconnpilot.py add -n myserver --host 192.168.1.100 -u admin

# With all options
python3 sshconnpilot.py add -n web-prod \
  --host web.example.com \
  -u ubuntu \
  -p 2222 \
  -i ~/.ssh/id_rsa \
  -d "Production web server" \
  -t "production,web,aws"
```

#### Managing Hosts

```bash
# Show host details
python3 sshconnpilot.py show web-prod

# Update host
python3 sshconnpilot.py update web-prod --port 2222 --user root

# Remove host
python3 sshconnpilot.py remove web-prod

# List with filters
python3 sshconnpilot.py list --tag production
python3 sshconnpilot.py list --search web
```

#### AI Configuration Assistant

```bash
# Get smart configuration suggestions
python3 sshconnpilot.py suggest "AWS EC2 Ubuntu Docker host for microservices"

# Output example:
# 🤖 AI Configuration Assistant
#
# Based on your description: 'AWS EC2 Ubuntu Docker host for microservices'
#
# Suggested Configuration:
#   • name: my-server
#   • hostname: example.com
#   • user: ec2-user
#   • port: 22
#   • tags: ['aws', 'ubuntu', 'docker']
```

#### Statistics and History

```bash
# View connection statistics
python3 sshconnpilot.py stats

# View connection history
python3 sshconnpilot.py history --limit 50
```

#### Import/Export

```bash
# Export to JSON
python3 sshconnpilot.py export backup.json

# Export to OpenSSH config format
python3 sshconnpilot.py export ssh_config.txt --format ssh_config

# Import from JSON
python3 sshconnpilot.py import backup.json

# Import from SSH config
python3 sshconnpilot.py import ~/.ssh/config --format ssh_config
```

### 💡 Design Philosophy

**SSHConnPilot** was designed with these principles:

1. **Zero Dependencies**: Only uses Python standard library for maximum compatibility
2. **Security First**: Local encryption, strict file permissions (600/700)
3. **Developer Experience**: Beautiful, intuitive CLI with helpful feedback
4. **AI-Assisted**: Smart suggestions reduce configuration errors
5. **Unix Philosophy**: Do one thing well, integrate with existing workflows

### 📦 Packaging and Deployment

This is a **CLI tool/script project** - no compilation required.

```bash
# Direct usage
python3 sshconnpilot.py [command]

# Or install via pip
pip install -e .
sshconnpilot --version
sshcp --version  # Short alias
```

### 🤝 Contributing Guidelines

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository
2. Create a **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'feat: Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. Open a **Pull Request**

Please ensure:
- Code follows PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 🎉 项目介绍

**SSHConnPilot** 是一款轻量级、零依赖的 Python CLI 工具，专为每天需要管理多个 SSH 连接的开发者与系统管理员设计。它结合了 AI 辅助配置建议、安全凭证存储、连接分析统计和直观的界面，简化您的 SSH 工作流程。

**核心差异化特性：**
- 🤖 **AI 辅助配置**：基于服务器描述的智能建议
- 🔐 **安全凭证存储**：本地加密保护敏感数据
- 📊 **连接分析统计**：追踪使用模式与统计数据
- 🎯 **零依赖**：纯 Python 标准库实现
- 🌈 **精美终端界面**：彩色、直观的交互体验

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🤖 **AI 智能建议** | 从自然语言描述生成配置模板 |
| 🔐 **安全存储** | 类 AES 加密凭证，700 权限配置文件 |
| 📊 **统计分析** | 连接历史、使用统计、热门主机 |
| 🏷️ **标签系统** | 使用自定义标签组织和筛选主机 |
| 🔄 **导入导出** | 支持 JSON 和 OpenSSH 配置格式 |
| 🧪 **连接测试** | 无需完整登录即可测试 SSH 连通性 |
| 💻 **交互模式** | 类 Shell 交互界面，适合日常使用 |
| 🚀 **快速连接** | 一次性连接，无需保存到数据库 |

### 🚀 快速开始

#### 环境要求
- Python 3.8 或更高版本
- 已安装 SSH 客户端

#### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/SSHConnPilot.git
cd SSHConnPilot

# 安装（可选）
pip install -e .

# 或直接运行
python3 sshconnpilot.py
```

#### 基本用法

```bash
# 启动交互模式
python3 sshconnpilot.py

# 添加新主机
python3 sshconnpilot.py add -n web-server --host 192.168.1.10 -u ubuntu -t "production,web"

# 列出所有主机
python3 sshconnpilot.py list

# 连接到主机
python3 sshconnpilot.py connect web-server

# 获取 AI 配置建议
python3 sshconnpilot.py suggest "AWS EC2 Ubuntu production server"

# 快速连接（不保存）
python3 sshconnpilot.py quick --host server.com -u root
```

### 📖 详细使用指南

#### 添加主机

```bash
# 基础用法
python3 sshconnpilot.py add -n myserver --host 192.168.1.100 -u admin

# 完整选项
python3 sshconnpilot.py add -n web-prod \
  --host web.example.com \
  -u ubuntu \
  -p 2222 \
  -i ~/.ssh/id_rsa \
  -d "Production web server" \
  -t "production,web,aws"
```

#### 管理主机

```bash
# 显示主机详情
python3 sshconnpilot.py show web-prod

# 更新主机
python3 sshconnpilot.py update web-prod --port 2222 --user root

# 删除主机
python3 sshconnpilot.py remove web-prod

# 带筛选的列表
python3 sshconnpilot.py list --tag production
python3 sshconnpilot.py list --search web
```

#### AI 配置助手

```bash
# 获取智能配置建议
python3 sshconnpilot.py suggest "AWS EC2 Ubuntu Docker host for microservices"
```

#### 统计与历史

```bash
# 查看连接统计
python3 sshconnpilot.py stats

# 查看连接历史
python3 sshconnpilot.py history --limit 50
```

#### 导入导出

```bash
# 导出为 JSON
python3 sshconnpilot.py export backup.json

# 导出为 OpenSSH 配置格式
python3 sshconnpilot.py export ssh_config.txt --format ssh_config

# 从 JSON 导入
python3 sshconnpilot.py import backup.json

# 从 SSH 配置导入
python3 sshconnpilot.py import ~/.ssh/config --format ssh_config
```

### 💡 设计理念

**SSHConnPilot** 遵循以下设计原则：

1. **零依赖**：仅使用 Python 标准库，确保最大兼容性
2. **安全优先**：本地加密、严格的文件权限（600/700）
3. **开发者体验**：美观、直观的 CLI 界面，提供有用的反馈
4. **AI 辅助**：智能建议减少配置错误
5. **Unix 哲学**：做好一件事，与现有工作流集成

### 📦 打包与部署

这是 **CLI 工具/脚本项目** - 无需编译。

```bash
# 直接使用
python3 sshconnpilot.py [command]

# 或通过 pip 安装
pip install -e .
sshconnpilot --version
sshcp --version  # 短别名
```

### 🤝 贡献指南

我们欢迎贡献！请遵循以下指南：

1. **Fork** 本仓库
2. 创建 **功能分支** (`git checkout -b feature/amazing-feature`)
3. **提交** 更改 (`git commit -m 'feat: Add amazing feature'`)
4. **推送** 到分支 (`git push origin feature/amazing-feature`)
5. 打开 **Pull Request**

### 📄 开源协议

本项目采用 MIT 许可证 - 详情请参见 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>
## 🇹
<a name="繁體中文"></a>
## 🇹

<a name="繁體中文"></a>
## 🇹

<a name="繁體中文"></a>
