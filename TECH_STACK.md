# 🛠️ 技术栈详解

## 📋 目录
1. [核心框架](#核心框架)
2. [AI和LLM](#ai和llm)
3. [数据库和存储](#数据库和存储)
4. [工具和库](#工具和库)
5. [部署和运维](#部署和运维)

---

## 核心框架

### FastAPI (v0.109.0)
**用途**：Web框架和REST API

**特点**：
- 异步支持（async/await）
- 自动API文档生成（Swagger UI）
- 数据验证（Pydantic）
- 高性能（基于Starlette）

**关键用法**：
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze")
async def analyze_culture(request: AnalyzeRequest):
    return await culture_analyst.analyze(request.village_info)
```

**文件位置**：`backend/main.py`, `backend/api/routes.py`

---

### Streamlit (前端)
**用途**：快速构建数据应用UI

**特点**：
- 无需前端框架，纯Python
- 热重载
- 内置组件库
- 快速原型开发

**关键用法**：
```python
import streamlit as st

st.title("乡村墙绘AI生成系统")
village_name = st.text_input("村落名称")
if st.button("分析"):
    response = requests.post("http://localhost:8000/api/analyze", ...)
    st.write(response.json())
```

**文件位置**：`frontend/app.py`

---

## AI和LLM

### CrewAI (v0.1.26)
**用途**：多Agent工作流编排

**特点**：
- 定义Agent角色和能力
- 编排Agent之间的协作
- 支持分步执行和完整工作流
- 进度回调机制

**关键概念**：
```python
from crewai import Agent, Task, Crew

# 定义Agent
analyst = Agent(
    role="文化研究专家",
    goal="分析乡村文化特色",
    backstory="资深的乡村文化研究者",
    tools=[search_tool, analysis_tool]
)

# 定义Task
analyze_task = Task(
    description="分析村落的文化特色",
    agent=analyst,
    expected_output="详细的文化分析报告"
)

# 编排Crew
crew = Crew(
    agents=[analyst],
    tasks=[analyze_task],
    verbose=True
)

result = crew.kickoff()
```

**文件位置**：`backend/agents/crew_manager.py`

---

### LangChain (v0.1.0)
**用途**：LLM应用框架

**特点**：
- Agent实现和工具调用
- Memory管理
- Chain编排
- 提示模板

**关键用法**：
```python
from langchain.agents import Tool, AgentExecutor, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI

# 定义工具
tools = [
    Tool(
        name="search_knowledge",
        func=search_villages,
        description="搜索村落知识库"
    )
]

# 创建Agent
memory = ConversationBufferMemory(memory_key="chat_history")
agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    memory=memory
)

# 执行
result = agent.run("分析西递村的文化特色")
```

**文件位置**：`backend/agents/`

---

### 通义千问 (Qwen)
**用途**：大语言模型

**模型**：`qwen-plus`

**特点**：
- 中文理解能力强
- 支持长文本
- 低延迟
- 成本低

**API调用**：
```python
from dashscope import Generation

response = Generation.call(
    model='qwen-plus',
    messages=[
        {'role': 'system', 'content': '你是一位文化研究专家'},
        {'role': 'user', 'content': '分析西递村的文化特色'}
    ],
    temperature=0.7,
    max_tokens=2000
)

print(response.output.text)
```

**文件位置**：`backend/services/llm_service.py`

---

### 通义万相 (Wanx)
**用途**：文本到图像生成

**模型**：`wanx-v1`

**特点**：
- 支持中文Prompt
- 多种风格
- 高质量输出
- 快速生成

**API调用**：
```python
from dashscope import ImageSynthesis

response = ImageSynthesis.call(
    model='wanx-v1',
    prompt='A traditional Chinese mural painting...',
    negative_prompt='low quality, blurry',
    style='<chinese-painting>',
    size='1024*1024',
    n=1
)

image_url = response.output.results[0].url
```

**文件位置**：`backend/services/image_service.py`

---

## 数据库和存储

### ChromaDB (v0.4.22)
**用途**：向量数据库

**特点**：
- 轻量级，无需单独部署
- 支持向量相似度搜索
- 支持元数据过滤
- 内置Embedding模型

**关键用法**：
```python
import chromadb

# 初始化
client = chromadb.Client()

# 创建集合
collection = client.create_collection(
    name="villages_knowledge",
    metadata={"hnsw:space": "cosine"}
)

# 添加文档
collection.add(
    ids=["village_001"],
    documents=["西递村位于安徽省黄山市..."],
    metadatas=[{"name": "西递村"}]
)

# 搜索
results = collection.query(
    query_texts=["徽派建筑特色"],
    n_results=3
)
```

**文件位置**：`backend/services/chromadb_service.py`

---

### Sentence Transformers
**用途**：文本向量化

**模型**：`paraphrase-multilingual-MiniLM-L12-v2`

**特点**：
- 多语言支持
- 轻量级
- 高效率
- 语义理解

**用法**：
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 向量化
embeddings = model.encode([
    "西递村的徽派建筑",
    "传统文化特色"
])

# 计算相似度
from sklearn.metrics.pairwise import cosine_similarity
similarity = cosine_similarity([embeddings[0]], [embeddings[1]])
```

**集成**：ChromaDB内置使用

---

## 工具和库

### Pydantic (v2.x)
**用途**：数据验证和设置管理

**特点**：
- 类型检查
- 自动验证
- 错误提示清晰
- 支持复杂数据结构

**关键用法**：
```python
from pydantic import BaseModel, Field, validator

class VillageInfo(BaseModel):
    name: str = Field(..., description="村落名称")
    location: str = Field(..., description="地理位置")
    industry: str = Field(..., description="主要产业")
    history: str = Field(..., description="历史背景")
    
    @validator('name')
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('村落名称不能为空')
        return v

# 使用
village = VillageInfo(
    name="西递村",
    location="安徽省黄山市",
    industry="旅游",
    history="明清古村落"
)
```

**文件位置**：`backend/api/models.py`, `backend/core/config.py`

---

### Loguru
**用途**：日志管理

**特点**：
- 简洁的API
- 自动文件轮转
- 彩色输出
- 结构化日志

**关键用法**：
```python
from loguru import logger

# 配置
logger.add(
    "logs/backend.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO"
)

# 使用
logger.info("应用启动")
logger.error("发生错误", exc_info=True)
logger.debug("调试信息")
```

**文件位置**：`backend/main.py`

---

### Python-dotenv
**用途**：环境变量管理

**特点**：
- 从.env文件加载
- 支持注释
- 类型转换

**关键用法**：
```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("DASHSCOPE_API_KEY")
port = int(os.getenv("BACKEND_PORT", 8000))
```

**文件位置**：`backend/core/config.py`

---

### Requests
**用途**：HTTP客户端

**特点**：
- 简洁的API
- 自动处理JSON
- 超时控制
- 重试机制

**关键用法**：
```python
import requests

response = requests.post(
    "https://api.example.com/data",
    json={"key": "value"},
    timeout=30,
    headers={"Authorization": "Bearer token"}
)

data = response.json()
```

**文件位置**：`backend/services/`

---

## 部署和运维

### Uvicorn
**用途**：ASGI服务器

**特点**：
- 高性能
- 支持热重载
- 支持多进程
- 支持SSL

**启动命令**：
```bash
# 开发模式
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn backend.main:app --workers 4 --host 0.0.0.0 --port 8000
```

---

### Gunicorn
**用途**：WSGI应用服务器（生产环境）

**配置**：
```bash
gunicorn -w 4 -b 0.0.0.0:8000 backend.main:app
```

---

### Docker
**用途**：容器化部署

**Dockerfile示例**：
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📊 依赖关系图

```
FastAPI
├── Starlette (Web框架)
├── Pydantic (数据验证)
└── Uvicorn (ASGI服务器)

CrewAI
├── LangChain (Agent框架)
├── Pydantic (数据模型)
└── 通义千问 (LLM)

LangChain
├── Pydantic (数据模型)
├── Requests (HTTP客户端)
└── 向量数据库 (ChromaDB)

ChromaDB
├── Sentence Transformers (Embedding)
└── SQLite (本地存储)

通义千问/万相
└── DashScope SDK

Streamlit
├── Requests (HTTP客户端)
└── Pandas (数据处理)
```

---

## 🔄 版本兼容性

| 组件 | 版本 | Python版本 | 备注 |
|------|------|-----------|------|
| FastAPI | 0.109.0 | 3.8+ | 最新稳定版 |
| CrewAI | 0.1.26 | 3.9+ | 实验性功能 |
| LangChain | 0.1.0 | 3.8+ | 快速迭代 |
| ChromaDB | 0.4.22 | 3.8+ | 向量DB |
| Streamlit | 1.28+ | 3.8+ | 前端框架 |
| Pydantic | 2.x | 3.8+ | 数据验证 |
| Python | 3.10+ | - | 推荐版本 |

---

## 📦 完整依赖列表

```
# 核心框架
fastapi==0.109.0
uvicorn[standard]==0.27.0
starlette==0.35.0

# AI和LLM
crewai==0.1.26
langchain==0.1.0
dashscope==1.14.0

# 数据库
chromadb==0.4.22
sentence-transformers==2.2.2

# 前端
streamlit==1.28.0

# 工具库
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
requests==2.31.0
loguru==0.7.2

# 开发工具
pytest==7.4.3
black==23.12.0
mypy==1.7.1
```

---

## 🚀 性能指标

| 组件 | 性能 | 备注 |
|------|------|------|
| FastAPI | <100ms | 单个请求 |
| ChromaDB检索 | <500ms | 1000个文档 |
| LLM调用 | 2-5s | 通义千问 |
| 图像生成 | 10-30s | 通义万相 |
| 总流程 | 15-40s | 完整工作流 |

---

## 💾 存储需求

| 组件 | 大小 | 备注 |
|------|------|------|
| ChromaDB | ~100MB | 1000个文档 |
| 生成图像 | ~2MB | 单张1024x1024 |
| 日志文件 | ~50MB | 每月 |
| 模型缓存 | ~500MB | Embedding模型 |

---

**最后更新**: 2025-10-16  
**版本**: 1.0.0

