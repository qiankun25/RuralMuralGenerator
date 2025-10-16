# ⚡ 快速参考指南

## 🚀 快速启动

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
# Streamlit
streamlit run frontend/app.py --server.port 8501
```

### 初始化知识库
```bash
python scripts/init_chromadb.py
```

---

## 📡 API快速参考

### 1. 健康检查
```bash
GET http://localhost:8000/api/health

# 响应
{
  "status": "healthy",
  "version": "1.0.0",
  "api_keys_configured": {"dashscope": true},
  "chromadb_status": "healthy (5 documents)"
}
```

### 2. 文化分析
```bash
POST http://localhost:8000/api/analyze
Content-Type: application/json

{
  "village_info": {
    "name": "西递村",
    "location": "安徽省黄山市黟县",
    "industry": "旅游、徽派建筑保护",
    "history": "明清古村落"
  }
}

# 响应
{
  "status": "success",
  "culture_analysis": "## 核心文化元素\n...",
  "data_sources": ["ChromaDB知识库", "政府开放数据", "通义千问AI"]
}
```

### 3. 设计方案生成
```bash
POST http://localhost:8000/api/design
Content-Type: application/json

{
  "culture_analysis": "## 核心文化元素\n...",
  "user_preference": "偏好传统风格"
}

# 响应
{
  "status": "success",
  "design_options": "## 方案A\n...",
  "num_options": 3
}
```

### 4. 图像生成（异步）
```bash
POST http://localhost:8000/api/generate-image
Content-Type: application/json

{
  "design_option": "## 方案A\n...",
  "style_preference": "traditional",
  "image_prompt": "可选的自定义Prompt"
}

# 响应（立即返回）
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "progress": 0
}
```

### 5. 查询任务状态
```bash
GET http://localhost:8000/api/task/550e8400-e29b-41d4-a716-446655440000

# 响应
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "result": {
    "images": [{"url": "...", "local_path": "..."}]
  }
}
```

### 6. 设计优化
```bash
POST http://localhost:8000/api/refine-design
Content-Type: application/json

{
  "original_design": "## 方案A\n...",
  "user_feedback": "希望更加现代一些"
}

# 响应
{
  "status": "success",
  "refined_design": "## 优化后的方案A\n..."
}
```

---

## 📁 项目结构速览

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
    ├── BACKEND_SUMMARY.md      # 后端总结
    ├── BACKEND_ARCHITECTURE.md # 架构详解
    ├── BACKEND_PROCESSING_LOGIC.md # 处理逻辑
    └── BACKEND_CODE_EXAMPLES.md # 代码示例
```

---

## 🔑 关键配置

### .env 文件
```bash
# LLM API
DASHSCOPE_API_KEY=sk-xxx

# 政府API
GOVERNMENT_API_KEY=xxx
GOVERNMENT_API_BASE_URL=https://api.example.gov.cn

# 数据库
CHROMADB_PATH=./data/chromadb

# 应用
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=8501

# LLM模型
LLM_MODEL_NAME=qwen-plus
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# 图像生成
IMAGE_OUTPUT_DIR=./data/generated_images
DEFAULT_IMAGE_STYLE=<chinese-painting>
```

---

## 🔍 常见问题排查

### 问题1：API密钥未配置
**症状**：健康检查返回 `api_keys_configured: false`

**解决**：
```bash
# 检查 .env 文件
cat .env

# 确保包含
DASHSCOPE_API_KEY=sk-xxx
```

### 问题2：ChromaDB连接失败
**症状**：`chromadb_status: "error"`

**解决**：
```bash
# 重新初始化
python scripts/init_chromadb.py

# 检查数据目录
ls -la data/chromadb/
```

### 问题3：图像生成返回Mock图像
**症状**：生成的图像是占位符

**解决**：
```bash
# 检查API密钥
echo $DASHSCOPE_API_KEY

# 检查网络连接
ping api.dashscope.aliyun.com
```

### 问题4：任务一直处于pending状态
**症状**：`GET /api/task/{id}` 返回 `status: pending`

**解决**：
```bash
# 检查后台任务
# 查看日志文件
tail -f logs/backend.log

# 重启后端
python backend/main.py
```

---

## 📊 数据模型速览

### VillageInfo（村落信息）
```python
{
  "name": str,           # 村落名称
  "location": str,       # 地理位置
  "industry": str,       # 主要产业
  "history": str,        # 历史背景
  "custom_info": str     # 其他信息（可选）
}
```

### AnalyzeRequest（分析请求）
```python
{
  "village_info": VillageInfo
}
```

### DesignRequest（设计请求）
```python
{
  "culture_analysis": str,    # 文化分析报告
  "user_preference": str      # 用户偏好
}
```

### ImageGenerationRequest（图像生成请求）
```python
{
  "design_option": str,           # 设计方案
  "style_preference": str,        # 风格偏好
  "image_prompt": str             # 自定义Prompt（可选）
}
```

---

## 🛠️ 开发常用命令

### 运行测试
```bash
pytest tests/ -v
```

### 代码格式化
```bash
black backend/
```

### 类型检查
```bash
mypy backend/
```

### 查看API文档
```
http://localhost:8000/docs
http://localhost:8000/redoc
```

### 查看日志
```bash
tail -f logs/backend.log
```

---

## 📚 文档导航

| 文档 | 内容 |
|------|------|
| **BACKEND_SUMMARY.md** | 后端系统总体概览 |
| **BACKEND_ARCHITECTURE.md** | 详细的架构设计 |
| **BACKEND_PROCESSING_LOGIC.md** | 处理逻辑和算法 |
| **BACKEND_CODE_EXAMPLES.md** | 代码示例和调用流程 |
| **QUICK_REFERENCE.md** | 本文档 - 快速参考 |

---

## 🎯 工作流速查

### 完整用户流程
```
1. 用户输入村落信息
   ↓
2. 后端分析文化特色
   ├─ 检索知识库
   ├─ 查询政府数据
   └─ LLM分析
   ↓
3. 生成3个设计方案
   ├─ 检索设计案例
   ├─ LLM生成
   └─ 内容审核
   ↓
4. 用户选择方案
   ↓
5. 后台异步生成图像
   ├─ 优化Prompt
   ├─ 调用API
   └─ 下载存储
   ↓
6. 展示结果
```

---

## 💡 性能优化建议

### 1. 启用缓存
```python
# 在 config.py 中
ENABLE_CACHE = True
CACHE_TTL = 3600  # 1小时
```

### 2. 使用Redis（生产环境）
```python
# 替换内存任务存储
from redis import Redis
tasks_storage = Redis(host='localhost', port=6379)
```

### 3. 批量初始化知识库
```bash
python scripts/init_chromadb.py --batch-size 100
```

### 4. 启用异步日志
```python
# 在 main.py 中
logger.enable("backend", sink="logs/backend.log", 
              serialize=True, rotation="500 MB")
```

---

## 🔗 相关资源

- **FastAPI文档**: https://fastapi.tiangolo.com/
- **CrewAI文档**: https://docs.crewai.com/
- **LangChain文档**: https://python.langchain.com/
- **ChromaDB文档**: https://docs.trychroma.com/
- **通义千问API**: https://dashscope.aliyun.com/
- **通义万相API**: https://dashscope.aliyun.com/

---

## 📞 获取帮助

### 查看系统日志
```bash
# 实时查看
tail -f logs/backend.log

# 查看最后100行
tail -100 logs/backend.log

# 搜索错误
grep "ERROR" logs/backend.log
```

### 调试模式
```bash
# 启用调试日志
export LOG_LEVEL=DEBUG
python backend/main.py
```

### 性能分析
```bash
# 使用cProfile
python -m cProfile -s cumtime backend/main.py
```

---

**最后更新**: 2025-10-16  
**版本**: 1.0.0

