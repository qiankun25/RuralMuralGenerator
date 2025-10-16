# 🏡 乡村墙绘AI生成系统 - 后端架构详解

## 📋 目录
1. [系统架构概览](#系统架构概览)
2. [核心层级说明](#核心层级说明)
3. [数据流处理](#数据流处理)
4. [关键模块详解](#关键模块详解)
5. [API接口说明](#api接口说明)

---

## 系统架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit前端 (8501)                      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI后端 (8000) - main.py                    │
│  ├─ CORS中间件配置                                           │
│  ├─ 日志系统（Loguru）                                       │
│  └─ 启动/关闭事件处理                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  API路由层   │  │  业务逻辑层  │  │  数据层      │
│ (routes.py)  │  │ (agents/)    │  │ (services/)  │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 核心层级说明

### 1️⃣ **FastAPI应用层** (`backend/main.py`)

**职责**：
- 创建FastAPI应用实例
- 配置CORS中间件（允许Streamlit跨域访问）
- 注册API路由
- 管理应用生命周期事件

**关键代码**：
```python
app = FastAPI(
    title="乡村墙绘AI生成系统",
    version="1.0.0"
)

# 启动事件：初始化ChromaDB、验证API密钥
@app.on_event("startup")
async def startup_event():
    chromadb_service.initialize()
    settings.validate_api_keys()
```

---

### 2️⃣ **API路由层** (`backend/api/routes.py`)

**职责**：
- 定义RESTful接口
- 处理HTTP请求/响应
- 管理异步任务

**核心接口**：

| 接口 | 方法 | 功能 | 类型 |
|------|------|------|------|
| `/api/health` | GET | 健康检查 | 同步 |
| `/api/analyze` | POST | 文化分析 | 同步 |
| `/api/design` | POST | 设计方案生成 | 同步 |
| `/api/generate-image` | POST | 图像生成 | 异步 |
| `/api/task/{task_id}` | GET | 查询任务状态 | 同步 |
| `/api/refine-design` | POST | 设计优化 | 同步 |

**异步任务管理**：
```python
tasks_storage: Dict[str, Dict] = {}  # 内存存储（生产环境用Redis）

# 任务状态流转：pending → processing → completed/failed
```

---

### 3️⃣ **业务逻辑层** (`backend/agents/`)

#### **文化分析Agent** (`culture_analyst.py`)

**处理流程**：
```
村落信息输入
    ↓
[步骤1] 从ChromaDB检索相关知识
    ↓
[步骤2] 查询政府开放数据
    ↓
[步骤3] 使用LLM进行深度分析
    ↓
输出：文化分析报告（Markdown格式）
```

**关键方法**：
- `analyze(village_info)` - 主分析方法
- `_retrieve_knowledge()` - 知识库检索
- `_query_government_data()` - 政府数据查询
- `_generate_analysis()` - LLM分析

#### **创意设计Agent** (`creative_designer.py`)

**处理流程**：
```
文化分析报告 + 用户偏好
    ↓
[步骤1] 检索设计案例参考
    ↓
[步骤2] 使用LLM生成3个设计方案
    ↓
[步骤3] 敏感词检测
    ↓
输出：3个设计方案（Markdown格式）
```

**关键方法**：
- `generate_designs()` - 生成设计方案
- `extract_image_prompt()` - 提取图像Prompt
- `refine_design()` - 根据反馈优化设计

#### **图像生成Agent** (`image_generator.py`)

**处理流程**：
```
图像Prompt + 风格偏好
    ↓
调用图像生成服务
    ↓
输出：生成的图像（本地路径或URL）
```

#### **CrewAI工作流管理器** (`crew_manager.py`)

**职责**：
- 编排多个Agent的协作流程
- 支持分步执行和完整工作流
- 提供进度回调机制

---

### 4️⃣ **服务层** (`backend/services/`)

#### **ChromaDB服务** (`chromadb_service.py`)

**功能**：
- 向量数据库初始化和管理
- 村落知识库管理
- 设计案例库管理
- 语义检索

**关键方法**：
```python
initialize()              # 初始化ChromaDB
add_villages()           # 添加村落知识
add_design_cases()       # 添加设计案例
search_villages()        # 搜索村落知识
search_design_cases()    # 搜索设计案例
```

**两个集合**：
- `villages_knowledge` - 村落文化知识库
- `design_cases` - 墙绘设计案例库

#### **LLM服务** (`llm_service.py`)

**功能**：
- 通义千问API封装
- 文本生成和对话
- 专用接口（文化分析、设计生成、Prompt优化）

**关键方法**：
```python
chat()                    # 通用对话
generate_text()          # 文本生成
analyze_culture()        # 文化分析专用
generate_design_options() # 设计生成专用
refine_image_prompt()    # Prompt优化
```

#### **图像生成服务** (`image_service.py`)

**功能**：
- 通义万相API封装
- 图像下载和存储
- Mock图像降级方案

**关键方法**：
```python
generate_image()         # 生成图像
generate_mural_image()   # 墙绘图像生成（高级）
_download_image()        # 下载图像
_get_mock_image()        # Mock图像降级
```

#### **政府数据服务** (`government_service.py`)

**功能**：
- 政府开放数据API调用
- Mock数据支持
- 缓存机制

---

### 5️⃣ **工具层** (`backend/tools/`)

#### **ChromaDB工具** (`chromadb_tool.py`)

LangChain Tool，用于Agent调用：
- `search_village_knowledge()` - 搜索村落知识
- `search_design_cases()` - 搜索设计案例

#### **政府API工具** (`government_api_tool.py`)

LangChain Tool，用于Agent调用：
- `query_government_data()` - 查询政府数据

#### **敏感词检测工具** (`sensitive_check_tool.py`)

LangChain Tool，用于内容审核：
- `check_text()` - 检测敏感词

---

### 6️⃣ **配置层** (`backend/core/config.py`)

**功能**：
- 使用Pydantic Settings管理环境变量
- 验证API密钥
- 确保必要目录存在

**配置分类**：
- LLM API配置（DashScope）
- 外部数据API配置（政府数据）
- 数据库配置（ChromaDB、SQLite）
- 应用配置（主机、端口、日志）
- 图像生成配置
- 敏感词检测配置

---

## 数据流处理

### 完整工作流数据流

```
用户输入（村落信息）
    ↓
[API] POST /api/analyze
    ↓
[Agent] 文化分析Agent
    ├─ [Service] ChromaDB检索村落知识
    ├─ [Service] 政府API查询数据
    └─ [Service] LLM进行深度分析
    ↓
返回：文化分析报告
    ↓
[API] POST /api/design
    ↓
[Agent] 创意设计Agent
    ├─ [Service] ChromaDB检索设计案例
    ├─ [Service] LLM生成3个设计方案
    └─ [Tool] 敏感词检测
    ↓
返回：3个设计方案
    ↓
[API] POST /api/generate-image (异步)
    ↓
[后台任务] _generate_image_task
    ├─ [Agent] 图像生成Agent
    ├─ [Service] 图像生成服务
    └─ 更新任务状态
    ↓
[API] GET /api/task/{task_id}
    ↓
返回：任务状态和结果
```

---

## 关键模块详解

### 配置管理流程

```python
# 1. 从.env文件加载配置
settings = Settings()

# 2. 验证API密钥
api_keys_status = settings.validate_api_keys()

# 3. 确保目录存在
settings.ensure_directories()
```

### 知识库初始化流程

```python
# 1. 启动时初始化ChromaDB
chromadb_service.initialize()

# 2. 加载村落知识和设计案例
# 通过 scripts/init_chromadb.py 初始化

# 3. 支持向量检索
results = chromadb_service.search_villages(query)
```

### 异步任务处理流程

```python
# 1. 创建任务
task_id = str(uuid.uuid4())
tasks_storage[task_id] = {
    "status": "pending",
    "progress": 0,
    ...
}

# 2. 添加后台任务
background_tasks.add_task(_generate_image_task, ...)

# 3. 轮询查询状态
GET /api/task/{task_id}

# 4. 任务完成
tasks_storage[task_id]["status"] = "completed"
```

---

## API接口说明

### 1. 健康检查

```
GET /api/health

响应：
{
    "status": "healthy",
    "version": "1.0.0",
    "api_keys_configured": {
        "dashscope": true,
        "government": false,
        "wenxin": false
    },
    "chromadb_status": "healthy (5 documents)"
}
```

### 2. 文化分析

```
POST /api/analyze

请求：
{
    "village_info": {
        "name": "西递村",
        "location": "安徽省黄山市",
        "industry": "旅游、徽派建筑保护",
        "history": "明清古村落"
    }
}

响应：
{
    "status": "success",
    "culture_analysis": "## 核心文化元素\n...",
    "data_sources": ["ChromaDB知识库", "政府开放数据平台", "通义千问AI分析"]
}
```

### 3. 设计方案生成

```
POST /api/design

请求：
{
    "culture_analysis": "...",
    "user_preference": "偏好现代风格"
}

响应：
{
    "status": "success",
    "design_options": "## 方案A：传统文化风格\n...",
    "num_options": 3
}
```

### 4. 图像生成（异步）

```
POST /api/generate-image

请求：
{
    "design_option": "...",
    "style_preference": "traditional",
    "image_prompt": "可选的自定义Prompt"
}

响应：
{
    "task_id": "uuid",
    "status": "pending",
    "progress": 0,
    "message": "图像生成任务已创建"
}

查询状态：
GET /api/task/{task_id}

响应：
{
    "task_id": "uuid",
    "status": "completed",
    "progress": 100,
    "result": {
        "status": "success",
        "images": [{"url": "...", "local_path": "..."}]
    }
}
```

---

## 技术栈总结

| 层级 | 技术 | 版本 | 作用 |
|------|------|------|------|
| **Web框架** | FastAPI | 0.109.0 | RESTful API、异步处理 |
| **Agent编排** | CrewAI | 0.1.26 | 多Agent工作流管理 |
| **Agent实现** | LangChain | 0.1.0 | Agent逻辑、Memory、Tools |
| **向量数据库** | ChromaDB | 0.4.22 | RAG知识库 |
| **LLM** | 通义千问 | qwen-plus | 文本生成、分析 |
| **图像生成** | 通义万相 | wanx-v1 | 墙绘图像生成 |
| **日志** | Loguru | - | 结构化日志 |
| **配置** | Pydantic | - | 环境变量管理 |

---

## 总结

后端采用**分层架构**设计：
- **API层**：处理HTTP请求/响应
- **业务逻辑层**：多Agent协作处理
- **服务层**：封装外部API和数据库
- **工具层**：LangChain工具集
- **配置层**：统一配置管理

整个系统通过**RAG + LLM + 多Agent协作**实现乡村墙绘的个性化设计生成。

