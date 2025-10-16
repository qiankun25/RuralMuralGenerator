# 🎯 从这里开始 - 后端文档快速入门

欢迎来到**乡村墙绘AI生成系统**的后端文档！

本文档将帮助您快速了解和使用该系统。

---

## ⚡ 30秒快速了解

**这是什么？**
- 一个AI驱动的乡村墙绘设计生成系统
- 使用多Agent协作和RAG技术
- 支持文化分析、设计生成、图像生成

**核心功能？**
1. 📊 文化分析 - 分析村落文化特色
2. 🎨 设计生成 - 生成3个设计方案
3. 🖼️ 图像生成 - 生成高质量墙绘图像

**技术栈？**
- FastAPI + CrewAI + LangChain
- ChromaDB + 通义千问 + 通义万相

---

## 🚀 3分钟快速启动

### 1️⃣ 启动后端
```bash
python backend/main.py
```

### 2️⃣ 启动前端
```bash
streamlit run frontend/app.py --server.port 8501
```

### 3️⃣ 打开浏览器
```
http://localhost:8501
```

**完成！** 🎉

---

## 📚 选择您的学习路径

### 🟢 初级（30分钟）- 快速了解
**目标**：了解系统是什么，怎么用

**推荐阅读**：
1. 本文档（5分钟）
2. `BACKEND_SUMMARY.md` (15分钟)
3. `QUICK_REFERENCE.md` (10分钟)

**学习成果**：
- ✅ 理解系统架构
- ✅ 知道如何启动系统
- ✅ 了解主要功能

---

### 🟡 中级（2小时）- 深入学习
**目标**：理解系统设计和实现

**推荐阅读**：
1. `BACKEND_ARCHITECTURE.md` (20分钟)
2. `BACKEND_PROCESSING_LOGIC.md` (20分钟)
3. `TECH_STACK.md` (20分钟)
4. 项目源代码 (60分钟)

**学习成果**：
- ✅ 理解分层架构
- ✅ 理解业务逻辑
- ✅ 理解技术选型

---

### 🔴 高级（4小时）- 开发集成
**目标**：能够开发和扩展功能

**推荐阅读**：
1. `BACKEND_CODE_EXAMPLES.md` (20分钟)
2. 项目源代码 (60分钟)
3. API文档 (20分钟)
4. 实践开发 (120分钟)

**学习成果**：
- ✅ 能够调用API
- ✅ 能够修改代码
- ✅ 能够添加新功能

---

## 📖 文档导航

### 🎯 我想...

#### 快速上手
→ 阅读 `QUICK_REFERENCE.md`

#### 理解架构
→ 阅读 `BACKEND_ARCHITECTURE.md`

#### 理解逻辑
→ 阅读 `BACKEND_PROCESSING_LOGIC.md`

#### 查看代码示例
→ 阅读 `BACKEND_CODE_EXAMPLES.md`

#### 了解技术栈
→ 阅读 `TECH_STACK.md`

#### 快速查找内容
→ 使用 `DOCUMENTATION_INDEX.md`

#### 查看完整导航
→ 打开 `README_BACKEND.md`

---

## 🎓 核心概念速览

### 系统架构
```
API层 (FastAPI)
    ↓
Agent层 (CrewAI + LangChain)
    ↓
服务层 (Services)
    ↓
工具层 (LangChain Tools)
    ↓
外部资源 (API/DB)
```

### 工作流
```
用户输入
  ↓
文化分析 (同步)
  ↓
设计生成 (同步)
  ↓
用户选择
  ↓
图像生成 (异步)
  ↓
结果展示
```

### 关键技术
- **RAG** - 检索增强生成
- **多Agent** - 协作完成复杂任务
- **异步处理** - 提高系统性能
- **提示工程** - 优化LLM输出

---

## 🔑 6个核心API

| API | 功能 | 处理方式 |
|-----|------|---------|
| `POST /api/analyze` | 文化分析 | 同步 |
| `POST /api/design` | 设计生成 | 同步 |
| `POST /api/generate-image` | 图像生成 | 异步 |
| `GET /api/task/{id}` | 查询状态 | 同步 |
| `POST /api/refine-design` | 设计优化 | 同步 |
| `GET /api/health` | 健康检查 | 同步 |

**详细API文档**：`http://localhost:8000/docs`

---

## 💡 常见问题

### Q1：系统需要什么配置？
**A**：需要配置 `.env` 文件，包含API密钥等。详见 `QUICK_REFERENCE.md`

### Q2：如何添加知识库？
**A**：使用 `scripts/init_chromadb.py` 初始化。详见 `BACKEND_CODE_EXAMPLES.md`

### Q3：如何修改LLM参数？
**A**：修改 `backend/core/config.py`。详见 `TECH_STACK.md`

### Q4：如何部署到生产环境？
**A**：参考 `TECH_STACK.md` 的部署部分

### Q5：遇到问题怎么办？
**A**：查看 `QUICK_REFERENCE.md` 的常见问题排查

---

## 📊 系统特点

### ✨ 完整的AI工作流
- 文化分析 + 设计生成 + 图像生成
- 一站式解决方案

### 🚀 高性能设计
- 异步处理
- 缓存机制
- 批量操作

### 🛡️ 可靠的错误处理
- 降级方案
- 详细日志
- 异常捕获

### 📈 易于扩展
- 分层架构
- 模块化设计
- 清晰的接口

---

## 🎯 下一步

### 立即开始
```bash
# 1. 启动后端
python backend/main.py

# 2. 启动前端
streamlit run frontend/app.py --server.port 8501

# 3. 打开浏览器
# http://localhost:8501
```

### 深入学习
1. 选择您的学习路径（初级/中级/高级）
2. 按照推荐阅读顺序学习
3. 查看项目源代码

### 开发实践
1. 修改代码
2. 添加新功能
3. 部署到生产环境

---

## 📚 完整文档列表

| 文档 | 用途 | 阅读时间 |
|------|------|---------|
| **START_HERE.md** | 快速入门（本文档） | 5分钟 |
| **README_BACKEND.md** | 文档导航 | 15分钟 |
| **BACKEND_SUMMARY.md** | 系统总览 | 15分钟 |
| **BACKEND_ARCHITECTURE.md** | 架构详解 | 20分钟 |
| **BACKEND_PROCESSING_LOGIC.md** | 处理逻辑 | 20分钟 |
| **BACKEND_CODE_EXAMPLES.md** | 代码示例 | 20分钟 |
| **QUICK_REFERENCE.md** | 快速参考 | 15分钟 |
| **TECH_STACK.md** | 技术栈 | 20分钟 |
| **DOCUMENTATION_INDEX.md** | 快速查找 | 10分钟 |
| **DOCUMENTATION_COMPLETE.md** | 完成报告 | 10分钟 |

---

## 🔗 快速链接

### 本地资源
- 后端API：`http://localhost:8000`
- API文档：`http://localhost:8000/docs`
- 前端应用：`http://localhost:8501`

### 项目文件
- 后端代码：`backend/`
- 前端代码：`frontend/`
- 启动脚本：`scripts/`
- 数据目录：`data/`

### 外部资源
- FastAPI：https://fastapi.tiangolo.com/
- CrewAI：https://docs.crewai.com/
- LangChain：https://python.langchain.com/
- ChromaDB：https://docs.trychroma.com/

---

## 💬 获取帮助

### 快速查找
- 使用 `DOCUMENTATION_INDEX.md` 快速查找内容

### 常见问题
- 查看 `QUICK_REFERENCE.md` 的常见问题排查

### 代码示例
- 参考 `BACKEND_CODE_EXAMPLES.md`

### 架构理解
- 阅读 `BACKEND_ARCHITECTURE.md`

---

## ✅ 检查清单

启动前，请确保：
- [ ] Python 3.10+ 已安装
- [ ] 依赖已安装 (`pip install -r requirements.txt`)
- [ ] `.env` 文件已配置
- [ ] ChromaDB 已初始化 (`python scripts/init_chromadb.py`)

---

## 🎉 准备好了吗？

### 选择您的起点：

**🟢 我是新手**
→ 阅读 `BACKEND_SUMMARY.md`

**🟡 我想深入学习**
→ 阅读 `BACKEND_ARCHITECTURE.md`

**🔴 我想开发功能**
→ 阅读 `BACKEND_CODE_EXAMPLES.md`

**⚡ 我想快速查询**
→ 使用 `QUICK_REFERENCE.md`

---

**祝您使用愉快！** 🚀

有任何问题，请参考相应的文档或查看项目源代码。

**开始探索吧！** 👉 [打开 README_BACKEND.md](README_BACKEND.md)

