# 💻 后端关键代码示例和调用流程

## 📋 目录
1. [API调用示例](#api调用示例)
2. [核心类和方法](#核心类和方法)
3. [数据模型](#数据模型)
4. [调用链路追踪](#调用链路追踪)

---

## API调用示例

### 1. 文化分析API

**请求**：
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "village_info": {
      "name": "西递村",
      "location": "安徽省黄山市黟县",
      "industry": "旅游、徽派建筑保护",
      "history": "明清古村落，以马头墙和木雕闻名"
    }
  }'
```

**响应**：
```json
{
  "status": "success",
  "message": "文化分析完成",
  "culture_analysis": "## 核心文化元素\n- 徽派建筑...",
  "data_sources": [
    "ChromaDB知识库",
    "政府开放数据平台",
    "通义千问AI分析"
  ],
  "timestamp": "2025-10-16T10:30:00"
}
```

### 2. 设计方案生成API

**请求**：
```bash
curl -X POST "http://localhost:8000/api/design" \
  -H "Content-Type: application/json" \
  -d '{
    "culture_analysis": "## 核心文化元素\n...",
    "user_preference": "偏好传统风格"
  }'
```

**响应**：
```json
{
  "status": "success",
  "message": "设计方案生成完成",
  "design_options": "## 方案A：传统文化风格\n...",
  "num_options": 3,
  "timestamp": "2025-10-16T10:35:00"
}
```

### 3. 图像生成API（异步）

**请求**：
```bash
curl -X POST "http://localhost:8000/api/generate-image" \
  -H "Content-Type: application/json" \
  -d '{
    "design_option": "## 方案A：传统文化风格\n...",
    "style_preference": "traditional",
    "image_prompt": "可选的自定义Prompt"
  }'
```

**响应**（立即返回）：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "progress": 0,
  "message": "图像生成任务已创建",
  "created_at": "2025-10-16T10:40:00",
  "updated_at": "2025-10-16T10:40:00"
}
```

### 4. 查询任务状态API

**请求**：
```bash
curl -X GET "http://localhost:8000/api/task/550e8400-e29b-41d4-a716-446655440000"
```

**响应（处理中）**：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 50,
  "updated_at": "2025-10-16T10:41:00"
}
```

**响应（完成）**：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "result": {
    "status": "success",
    "images": [
      {
        "url": "https://...",
        "local_path": "./data/generated_images/generated_20251016_104200_0.png"
      }
    ],
    "prompt": "A traditional Chinese mural painting...",
    "style": "traditional"
  },
  "updated_at": "2025-10-16T10:42:00"
}
```

---

## 核心类和方法

### 1. ChromaDBService

```python
from backend.services import chromadb_service

# 初始化
chromadb_service.initialize()

# 添加村落知识
chromadb_service.add_villages([
    {
        "id": "village_001",
        "content": "西递村位于安徽省黄山市...",
        "metadata": {"name": "西递村", "province": "安徽"}
    }
])

# 搜索村落知识
results = chromadb_service.search_villages(
    query="徽派建筑特色",
    n_results=3
)
# 返回：{
#   "ids": ["village_001", ...],
#   "documents": ["西递村位于...", ...],
#   "metadatas": [{...}, ...],
#   "distances": [0.15, ...]
# }

# 搜索设计案例
results = chromadb_service.search_design_cases(
    query="传统风格设计",
    n_results=2
)
```

### 2. LLMService

```python
from backend.services import llm_service

# 简单文本生成
result = llm_service.generate_text(
    prompt="请介绍徽派建筑的特点",
    system_prompt="你是建筑专家",
    temperature=0.7,
    max_tokens=500
)

# 文化分析专用
analysis = llm_service.analyze_culture(
    village_info={
        "name": "西递村",
        "location": "安徽省黄山市",
        "industry": "旅游",
        "history": "明清古村落"
    },
    knowledge_context="【知识库检索结果】\n..."
)

# 生成设计方案
designs = llm_service.generate_design_options(
    culture_analysis="## 核心文化元素\n...",
    user_preference="偏好传统风格"
)

# 优化图像Prompt
optimized_prompt = llm_service.refine_image_prompt(
    design_description="## 方案A：传统文化风格\n..."
)
```

### 3. ImageGenerationService

```python
from backend.services import image_service

# 生成图像
result = image_service.generate_image(
    prompt="A traditional Chinese mural painting...",
    negative_prompt="low quality, blurry",
    style="<chinese-painting>",
    size="1024*1024",
    n=1
)
# 返回：{
#   "status": "success",
#   "images": [{"url": "...", "local_path": "..."}],
#   "prompt": "...",
#   "style": "..."
# }

# 生成墙绘图像（高级接口）
result = image_service.generate_mural_image(
    design_prompt="A traditional Chinese mural painting...",
    style_preference="traditional"  # traditional/modern/narrative
)
```

### 4. CultureAnalystAgent

```python
from backend.agents import culture_analyst

# 分析村落文化
analysis = culture_analyst.analyze({
    "name": "西递村",
    "location": "安徽省黄山市",
    "industry": "旅游、徽派建筑保护",
    "history": "明清古村落"
})
# 返回：Markdown格式的文化分析报告
```

### 5. CreativeDesignerAgent

```python
from backend.agents import creative_designer

# 生成设计方案
designs = creative_designer.generate_designs(
    culture_analysis="## 核心文化元素\n...",
    user_preference="偏好传统风格"
)
# 返回：包含3个设计方案的Markdown文本

# 提取图像Prompt
prompt = creative_designer.extract_image_prompt(
    design_option="## 方案A：传统文化风格\n..."
)

# 优化设计
refined = creative_designer.refine_design(
    original_design="## 方案A\n...",
    user_feedback="希望更加现代一些"
)
```

### 6. ImageGeneratorAgent

```python
from backend.agents import image_generator

# 生成图像
result = image_generator.generate(
    image_prompt="A traditional Chinese mural painting...",
    style_preference="traditional",
    size="1024*1024"
)
# 返回：{
#   "status": "success",
#   "images": [...],
#   "prompt": "...",
#   "style": "...",
#   "is_mock": False
# }

# 重新生成（根据调整要求）
result = image_generator.regenerate(
    original_prompt="A traditional Chinese mural painting...",
    adjustment="add more vibrant colors",
    style_preference="traditional"
)
```

---

## 数据模型

### 请求模型

```python
from backend.api.models import (
    VillageInfo,
    AnalyzeRequest,
    DesignRequest,
    ImageGenerationRequest,
    RefineDesignRequest
)

# 村落信息
village_info = VillageInfo(
    name="西递村",
    location="安徽省黄山市黟县",
    industry="旅游、徽派建筑保护",
    history="明清古村落，以马头墙和木雕闻名",
    custom_info="其他信息"
)

# 文化分析请求
analyze_req = AnalyzeRequest(village_info=village_info)

# 设计请求
design_req = DesignRequest(
    culture_analysis="## 核心文化元素\n...",
    user_preference="偏好传统风格"
)

# 图像生成请求
image_req = ImageGenerationRequest(
    design_option="## 方案A\n...",
    style_preference="traditional",
    image_prompt="可选的自定义Prompt"
)

# 设计优化请求
refine_req = RefineDesignRequest(
    original_design="## 方案A\n...",
    user_feedback="希望更加现代一些"
)
```

### 响应模型

```python
from backend.api.models import (
    AnalyzeResponse,
    DesignResponse,
    TaskStatusResponse,
    HealthCheckResponse
)

# 文化分析响应
analyze_resp = AnalyzeResponse(
    status="success",
    message="文化分析完成",
    culture_analysis="## 核心文化元素\n...",
    data_sources=["ChromaDB知识库", "政府开放数据平台", "通义千问AI分析"]
)

# 设计响应
design_resp = DesignResponse(
    status="success",
    message="设计方案生成完成",
    design_options="## 方案A\n...",
    num_options=3
)

# 任务状态响应
task_resp = TaskStatusResponse(
    task_id="uuid",
    status="completed",
    progress=100,
    result={...},
    error=None
)

# 健康检查响应
health_resp = HealthCheckResponse(
    status="healthy",
    version="1.0.0",
    api_keys_configured={"dashscope": True, "government": False},
    chromadb_status="healthy (5 documents)"
)
```

---

## 调用链路追踪

### 完整工作流调用链

```
前端 (Streamlit)
    │
    ├─→ POST /api/analyze
    │   └─→ routes.analyze_culture()
    │       └─→ culture_analyst.analyze()
    │           ├─→ chromadb_service.search_villages()
    │           ├─→ government_service.query_village_data_sync()
    │           └─→ llm_service.analyze_culture()
    │               └─→ Generation.call() [通义千问API]
    │
    ├─→ POST /api/design
    │   └─→ routes.generate_design()
    │       └─→ creative_designer.generate_designs()
    │           ├─→ chromadb_service.search_design_cases()
    │           ├─→ llm_service.generate_design_options()
    │           │   └─→ Generation.call() [通义千问API]
    │           └─→ sensitive_check_tool.check_text()
    │
    ├─→ POST /api/generate-image
    │   └─→ routes.generate_image()
    │       ├─→ 创建任务ID和存储
    │       └─→ background_tasks.add_task()
    │           └─→ _generate_image_task()
    │               ├─→ creative_designer.extract_image_prompt()
    │               │   └─→ llm_service.refine_image_prompt()
    │               └─→ image_generator.generate()
    │                   └─→ image_service.generate_mural_image()
    │                       ├─→ ImageSynthesis.call() [通义万相API]
    │                       └─→ _download_image()
    │
    └─→ GET /api/task/{task_id}
        └─→ routes.get_task_status()
            └─→ 返回 tasks_storage[task_id]
```

### 单个API调用的内部流程

**例：POST /api/analyze**

```
1. FastAPI接收请求
   ├─ 验证请求模型 (Pydantic)
   └─ 调用 routes.analyze_culture()

2. routes.analyze_culture()
   ├─ 记录日志
   ├─ 调用 culture_analyst.analyze()
   └─ 返回 AnalyzeResponse

3. culture_analyst.analyze()
   ├─ 调用 _retrieve_knowledge()
   │   └─ chromadb_service.search_villages()
   │       ├─ 向量化查询
   │       ├─ 计算相似度
   │       └─ 返回Top-3结果
   │
   ├─ 调用 _query_government_data()
   │   └─ government_service.query_village_data_sync()
   │       ├─ 调用政府API或返回Mock数据
   │       └─ 格式化结果
   │
   └─ 调用 _generate_analysis()
       └─ llm_service.analyze_culture()
           ├─ 构建System Prompt
           ├─ 构建User Prompt
           ├─ 调用 Generation.call()
           │   └─ 通义千问API
           └─ 返回分析报告

4. 返回响应给前端
```

---

## 关键配置

### 环境变量 (.env)

```bash
# LLM API
DASHSCOPE_API_KEY=sk-xxx

# 政府API
GOVERNMENT_API_KEY=xxx
GOVERNMENT_API_BASE_URL=https://api.example.gov.cn

# 数据库
CHROMADB_PATH=./data/chromadb
CHROMADB_COLLECTION_VILLAGES=villages_knowledge
CHROMADB_COLLECTION_DESIGNS=design_cases

# 应用配置
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_RELOAD=True
FRONTEND_PORT=8501

# LLM模型
LLM_MODEL_NAME=qwen-plus
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# 图像生成
IMAGE_OUTPUT_DIR=./data/generated_images
IMAGE_GENERATION_TIMEOUT=120
DEFAULT_IMAGE_STYLE=<chinese-painting>

# 日志
LOG_LEVEL=INFO
```

---

## 总结

后端通过**分层API设计**和**清晰的调用链路**实现：

1. **API层**：处理HTTP请求/响应
2. **Agent层**：编排业务逻辑
3. **Service层**：封装外部API和数据库
4. **Tool层**：提供LangChain工具

整个系统支持**同步和异步**处理，具有**良好的错误处理**和**降级方案**。

