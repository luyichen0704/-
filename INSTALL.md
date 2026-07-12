# 取证AI平台 - 安装指南

> 本指南将帮助您快速安装和配置取证AI平台

---

## 📋 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|----------|----------|
| 操作系统 | Windows 10/11 64位 | Windows 11 |
| Python | 3.8+ | 3.10+ |
| 内存 | 4GB | 8GB+ |
| 磁盘空间 | 2GB | 5GB+ |
| 网络 | 需要 | 稳定网络 |

---

## 🚀 快速安装（3步完成）

### 第一步：下载项目

**方式一：使用Git（推荐）**
```bash
git clone https://github.com/luyichen0704/forensic-ai-platform.git
```

**方式二：直接下载**
1. 访问 https://github.com/luyichen0704/forensic-ai-platform
2. 点击绿色 "Code" 按钮
3. 选择 "Download ZIP"
4. 解压到任意目录

### 第二步：运行安装向导

进入下载的文件夹，双击运行：

```
安装.bat
```

安装向导会自动：
- ✅ 检查系统环境
- ✅ 选择安装路径（默认D盘）
- ✅ 安装Python依赖
- ✅ 创建桌面快捷方式

### 第三步：启动使用

安装完成后，双击桌面快捷方式或运行：

```
start.bat
```

---

## 📖 详细安装步骤

### 1. 安装Python（如果未安装）

**下载Python：**
- 访问 https://www.python.org/downloads/
- 下载 Python 3.10 或更高版本
- 安装时 **务必勾选** "Add Python to PATH"

**验证安装：**
```bash
python --version
# 应显示: Python 3.10.x
```

### 2. 安装Git（如果未安装）

**下载Git：**
- 访问 https://git-scm.com/downloads
- 下载并安装

**验证安装：**
```bash
git --version
# 应显示: git version 2.x.x
```

### 3. 下载项目

```bash
# 打开命令行（Win+R，输入cmd）
# 进入想要安装的目录，例如D盘
cd /d D:\

# 克隆项目
git clone https://github.com/luyichen0704/forensic-ai-platform.git

# 进入项目目录
cd forensic-ai-platform
```

### 4. 运行安装向导

```bash
# 双击运行 安装.bat
# 或命令行执行
安装.bat
```

**安装向导界面：**

```
┌─────────────────────────────────────────────────────┐
│         🔍 取证AI平台 - 安装向导                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  步骤 1: 选择安装路径                               │
│  ┌─────────────────────────────────────────────┐   │
│  │ 安装路径: [D:\forensic-ai-platform      ][浏览] │   │
│  └─────────────────────────────────────────────┘   │
│  💡 建议安装到D盘或其他非系统盘                      │
│                                                     │
│  步骤 2: 安装选项                                   │
│  ☑️ 安装 Git (版本控制工具)                         │
│  ☑️ 安装 Python 依赖包                             │
│  ☑️ 安装取证工具 (sleuthkit, volatility等)          │
│                                                     │
│  步骤 3: 磁盘空间检查                               │
│  ✅ 可用空间: 156.3 GB / 238.5 GB (足够)            │
│                                                     │
│  [🚀 开始安装]                          [取消]      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 5. 配置API密钥

安装完成后，需要配置大模型API密钥：

```bash
# 编辑配置文件
notepad config\llm_config.json
```

**配置文件示例：**

```json
{
  "provider": "openai",
  "api_key": "your-api-key-here",
  "model": "gpt-4",
  "base_url": "https://api.openai.com/v1"
}
```

**支持的API：**

| 提供商 | 配置示例 |
|--------|----------|
| OpenAI | `"provider": "openai"` |
| Claude | `"provider": "claude"` |
| Ollama（本地） | `"provider": "ollama"` |

### 6. 启动平台

```bash
# 双击运行
start.bat

# 或命令行启动
python -m web.app
```

启动后访问：http://localhost:7860

---

## 🔧 常见问题

### Q1: 提示"python不是内部命令"

**原因：** Python未添加到PATH

**解决：**
1. 重新安装Python，勾选 "Add Python to PATH"
2. 或手动添加环境变量

### Q2: 安装依赖失败

**解决：**
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 端口被占用

**解决：**
```bash
# 修改端口
python -m web.app --port 7861
```

### Q4: Git克隆失败

**解决：**
```bash
# 使用代理或直接下载ZIP
# 访问 https://github.com/luyichen0704/forensic-ai-platform
# 点击 Code -> Download ZIP
```

### Q5: 更新失败

**解决：**
```bash
# 强制更新
git fetch origin
git reset --hard origin/main
```

---

## 📁 目录结构

```
forensic-ai-platform/
├── agent/                  # AI核心引擎
├── web/                    # Web界面
├── api/                    # API接口
├── plugins/                # 插件系统
├── skills/                 # 技能文档
├── cases/                  # 案例库
├── knowledge/              # 知识库
├── scripts/                # 工具脚本
├── config/                 # 配置文件
│   └── llm_config.json     # API配置
├── 安装.bat                # 安装向导
├── 更新工具.bat            # 更新工具
├── start.bat               # 启动脚本
└── requirements.txt        # Python依赖
```

---

## 🔄 项目更新

### 方式一：一键更新（推荐）

双击运行：

```
更新工具.bat
```

### 方式二：手动更新

```bash
git pull origin main
pip install -r requirements.txt
```

---

## 🎯 快速开始

### 1. 启动Web界面

```bash
start.bat
```

访问 http://localhost:7860

### 2. 使用API

```bash
# 启动API服务
python -m api.main

# 访问API文档
# http://localhost:8000/docs
```

### 3. 命令行使用

```bash
# 检查环境
python -m agent.doctor

# 分析证据
python -m agent.core --evidence evidence.E01 --question "找出恶意软件"
```

---

## 📚 更多资源

- **项目主页：** https://github.com/luyichen0704/forensic-ai-platform
- **问题反馈：** https://github.com/luyichen0704/forensic-ai-platform/issues
- **更新日志：** 查看项目根目录的 `UPDATE_GUIDE.md`

---

## 💡 获取帮助

如遇到问题，请按以下顺序尝试：

1. 查看本文档的"常见问题"部分
2. 搜索 GitHub Issues
3. 创建新 Issue 描述问题

---

**祝您使用愉快！** 🎉
