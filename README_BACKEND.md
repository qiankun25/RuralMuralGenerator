# 🎯 乡村墙绘AI生成系统 - 后端完整文档

## 📚 文档概览

本项目包含了完整的后端系统文档，帮助您快速理解和使用该系统。

### 📖 文档清单

| 文档 | 文件名 | 内容 | 适用场景 |
|------|--------|------|---------|
| **系统总结** | `BACKEND_SUMMARY.md` | 后端系统的整体概览、架构、工作流 | 快速了解系统 |
| **架构详解** | `BACKEND_ARCHITECTURE.md` | 详细的分层架构、数据流、API规范 | 深入理解设计 |
| **处理逻辑** | `BACKEND_PROCESSING_LOGIC.md` | 各阶段的详细处理流程、算法、优化 | 理解业务逻辑 |
| **代码示例** | `BACKEND_CODE_EXAMPLES.md` | API调用示例、核心类方法、数据模型 | 开发和集成 |
| **快速参考** | `QUICK_REFERENCE.md` | 启动命令、API速查、常见问题 | 日常开发 |
| **技术栈** | `TECH_STACK.md` | 框架、库、版本、依赖关系 | 技术选型和升级 |
| **本文档** | `README_BACKEND.md` | 文档导航和使用指南 | 文档入口 |

---

## 🚀 快速开始

### 第一步：了解系统
```
1. 阅读 BACKEND_SUMMARY.md
   └─ 了解系统整体架构和工作流
```

### 第二步：深入学习
```
2. 根据需要选择阅读：
   ├─ BACKEND_ARCHITECTURE.md (理解架构)
   ├─ BACKEND_PROCESSING_LOGIC.md (理解逻辑)
   └─ TECH_STACK.md (了解技术)
```

### 第三步：开发和集成
```
3. 参考以下文档：
   ├─ BACKEND_CODE_EXAMPLES.md (代码示例)
   ├─ QUICK_REFERENCE.md (API速查)
   └─ 项目源代码
```

---

## 📊 系统架构速览

### 分层架构
```
┌─────────────────────────────────────┐
│  API层 (FastAPI)                    │
│  6个REST接口                        │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│  Agent层 (CrewAI + LangChain)       │
│  3个专业Agent + 工作流编排          │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│  服务层 (Services)                  │
│  4个核心服务                        │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│  工具层 (LangChain Tools)           │
│  知识库、政府API、内容审核          │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│  外部资源                           │
│  ChromaDB、LLM、图像生成、政府API   │
└─────────────────────────────────────┘
```

---

## 🔄 核心工作流

### 5步完整流程

```
步骤1：用户输入
  └─ 村落名称、位置、产业、历史

步骤2：文化分析 (同步)
  ├─ ChromaDB检索相关知识
  ├─ 政府API查询数据
  └─ LLM深度分析 → 文化分析报告

步骤3：设计方案生成 (同步)
  ├─ ChromaDB检索设计案例
  ├─ LLM生成3个方案
  └─ 敏感词检测 → 3个设计方案

步骤4：用户选择方案
  └─ 前端展示3个方案供选择

步骤5：图像生成 (异步)
  ├─ 提取/优化Prompt
  ├─ 调用图像生成API
  └─ 下载存储 → 生成的图像
```

---

## 📡 API接口速览

### 6个核心接口

| 接口 | 方法 | 功能 | 处理方式 |
|------|------|------|---------|
| `/health` | GET | 系统健康检查 | 同步 |
| `/analyze` | POST | 文化分析 | 同步 |
| `/design` | POST | 设计方案生成 | 同步 |
| `/generate-image` | POST | 图像生成 | 异步 |
| `/task/{id}` | GET | 查询任务状态 | 同步 |
| `/refine-design` | POST | 设计优化 | 同步 |

**详细API文档**：见 `BACKEND_CODE_EXAMPLES.md`

---

## 🛠️ 技术栈

### 核心框架
- **FastAPI** - Web框架
- **CrewAI** - Agent编排
- **LangChain** - LLM应用框架
- **Streamlit** - 前端框架

### AI和LLM
- **通义千问** - 大语言模型
- **通义万相** - 图像生成
- **ChromaDB** - 向量数据库
- **Sentence Transformers** - 文本向量化

### 工具库
- **Pydantic** - 数据验证
- **Loguru** - 日志管理
- **Requests** - HTTP客户端
- **Python-dotenv** - 环境变量

**详细技术栈**：见 `TECH_STACK.md`

---

## 📁 项目结构

```
RuralMuralGenerator/
├── backend/
│   ├── main.py                 # FastAPI应用入口
│   ├── api/
│   │   ├── routes.py           # 6个API端点
│   │   └── models.py           # Pydantic数据模型
│   ├── agents/
│   │   ├── culture_analyst.py  # 文化分析Agent
│   │   ├── creative_designer.py # 创意设计Agent
│   │   ├── image_generator.py  # 图像生成Agent
│   │   └── crew_manager.py     # CrewAI编排
│   ├── services/
│   │   ├── chromadb_service.py # 向量数据库
│   │   ├── llm_service.py      # LLM服务
│   │   ├── image_service.py    # 图像生成服务
│   │   └── government_service.py # 政府数据服务
│   ├── tools/
│   │   └── chromadb_tool.py    # LangChain工具
│   └── core/
│       └── config.py           # 配置管理
├── frontend/
│   └── app.py                  # Streamlit应用
├── data/
│   ├── chromadb/               # 向量数据库存储
│   ├── generated_images/       # 生成的图像
│   └── sensitive_words.txt     # 敏感词库
├── scripts/
│   ├── init_chromadb.py        # 初始化知识库
│   └── start_backend.bat       # 启动脚本
└── docs/
    ├── BACKEND_SUMMARY.md
    ├── BACKEND_ARCHITECTURE.md
    ├── BACKEND_PROCESSING_LOGIC.md
    ├── BACKEND_CODE_EXAMPLES.md
    ├── QUICK_REFERENCE.md
    ├── TECH_STACK.md
    └── README_BACKEND.md
```

---

## 🚀 启动和部署

### 启动后端
```bash
# 方式1：直接运行
python backend/main.py

# 方式2：使用uvicorn
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 方式3：Windows批处理
scripts/start_backend.bat
```

### 启动前端
```bash
streamlit run frontend/app.py --server.port 8501
```

### 初始化知识库
```bash
python scripts/init_chromadb.py
```

### 访问应用
```
后端API: http://localhost:8000
API文档: http://localhost:8000/docs
前端应用: http://localhost:8501
```

---

## 🔑 关键概念

### RAG（检索增强生成）
通过向量数据库检索相关知识，增强LLM的生成能力。

**流程**：查询 → 向量化 → 检索 → 融合上下文 → LLM生成

### 多Agent协作
使用CrewAI编排多个Agent，分工协作完成复杂任务。

**Agent**：
- 文化分析Agent - 分析村落文化
- 创意设计Agent - 生成设计方案
- 图像生成Agent - 生成墙绘图像

### 异步处理
使用FastAPI的BackgroundTasks实现异步图像生成。

**优势**：不阻塞主线程，提高系统吞吐量

---

## 📊 数据流

### 完整数据流
```
用户输入
  ↓
API接收
  ↓
Agent处理
  ├─ 知识库检索
  ├─ 政府数据查询
  ├─ LLM分析/生成
  └─ 内容审核
  ↓
返回结果
  ↓
前端展示
```

---

## 🛡️ 错误处理

### 降级方案
- API调用失败 → 返回Mock数据
- 图像生成失败 → 返回占位符图像
- 知识库为空 → 使用通用知识
- 敏感词检测 → 仅记录警告

### 日志记录
所有操作都有详细的日志记录，便于调试和监控。

---

## 💡 最佳实践

### 1. 环境配置
```bash
# 创建 .env 文件
DASHSCOPE_API_KEY=sk-xxx
GOVERNMENT_API_KEY=xxx
CHROMADB_PATH=./data/chromadb
```

### 2. 知识库初始化
```bash
# 初始化ChromaDB
python scripts/init_chromadb.py
```

### 3. 日志监控
```bash
# 查看实时日志
tail -f logs/backend.log
```

### 4. 性能优化
- 启用缓存机制
- 使用异步处理
- 批量操作
- 定期清理日志

---

## 🔗 相关资源

### 官方文档
- [FastAPI](https://fastapi.tiangolo.com/)
- [CrewAI](https://docs.crewai.com/)
- [LangChain](https://python.langchain.com/)
- [ChromaDB](https://docs.trychroma.com/)

### API文档
- [通义千问](https://dashscope.aliyun.com/)
- [通义万相](https://dashscope.aliyun.com/)

### 本地文档
- 项目源代码
- API文档：`http://localhost:8000/docs`

---

## 📞 常见问题

### Q1：如何添加新的知识库文档？
**A**：见 `BACKEND_CODE_EXAMPLES.md` 中的 ChromaDBService 部分

### Q2：如何自定义LLM参数？
**A**：修改 `backend/core/config.py` 中的配置

### Q3：如何扩展Agent功能？
**A**：参考 `backend/agents/` 中的现有Agent实现

### Q4：如何部署到生产环境？
**A**：见 `TECH_STACK.md` 中的部署部分

---

## 📈 性能指标

| 操作 | 耗时 | 备注 |
|------|------|------|
| 文化分析 | 3-5s | 包括知识库检索和LLM分析 |
| 设计生成 | 2-4s | 包括案例检索和LLM生成 |
| 图像生成 | 10-30s | 异步处理 |
| 总流程 | 15-40s | 完整工作流 |

---

## 🎯 下一步

### 新手入门
1. 阅读 `BACKEND_SUMMARY.md`
2. 启动后端和前端
3. 尝试完整工作流

### 开发者
1. 阅读 `BACKEND_ARCHITECTURE.md`
2. 查看 `BACKEND_CODE_EXAMPLES.md`
3. 修改代码并测试

### 运维人员
1. 查看 `QUICK_REFERENCE.md`
2. 参考 `TECH_STACK.md`
3. 监控日志和性能

---

## 📝 文档维护

**最后更新**：2025-10-16  
**版本**：1.0.0  
**维护者**：AI Assistant

### 更新日志
- v1.0.0 (2025-10-16) - 初始版本，包含完整的后端文档

---

## 📄 许可证

本项目采用 MIT 许可证。

---

## 🙏 致谢

感谢所有贡献者和使用者的支持！

---

**开始探索吧！** 🚀

选择一个文档开始阅读：
- 🎯 [系统总结](BACKEND_SUMMARY.md)
- 🏗️ [架构详解](BACKEND_ARCHITECTURE.md)
- 🔄 [处理逻辑](BACKEND_PROCESSING_LOGIC.md)
- 💻 [代码示例](BACKEND_CODE_EXAMPLES.md)
- ⚡ [快速参考](QUICK_REFERENCE.md)
- 🛠️ [技术栈](TECH_STACK.md)

