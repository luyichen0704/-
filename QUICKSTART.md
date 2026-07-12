# 快速开始卡片

> 📋 打印此卡片，贴在显示器旁

---

## 🚀 3步安装

```
第1步: 下载
  → 访问 https://github.com/luyichen0704/forensic-ai-platform
  → 点击 Code → Download ZIP
  → 解压到 D:\

第2步: 安装
  → 双击 "安装.bat"
  → 选择路径: D:\forensic-ai-platform
  → 点击 "开始安装"

第3步: 启动
  → 双击桌面快捷方式 "取证AI平台"
  → 或双击 "start.bat"
```

---

## 📌 常用操作

| 操作 | 方法 |
|------|------|
| 启动平台 | 双击 `start.bat` |
| 更新项目 | 双击 `更新工具.bat` |
| 查看文档 | 打开 `INSTALL.md` |
| 配置API | 编辑 `config\llm_config.json` |

---

## 🔗 重要链接

- **项目地址：** https://github.com/luyichen0704/forensic-ai-platform
- **Web界面：** http://localhost:7860
- **API文档：** http://localhost:8000/docs

---

## ⚡ 快捷命令

```bash
# 启动Web界面
start.bat

# 启动API服务
python -m api.main

# 检查环境
python -m agent.doctor

# 更新项目
git pull origin main
```

---

## 🆘 遇到问题？

1. 双击 `更新工具.bat` 更新到最新版
2. 查看 `INSTALL.md` 常见问题
3. 提交 Issue: https://github.com/luyichen0704/forensic-ai-platform/issues

---

## 📦 项目结构

```
forensic-ai-platform/
├── 安装.bat          ← 首次安装
├── 更新工具.bat      ← 更新项目
├── start.bat         ← 启动程序
├── config/           ← 配置文件
├── agent/            ← AI引擎
├── web/              ← Web界面
├── cases/            ← 案例库
└── knowledge/        ← 知识库
```
