# API文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API前缀**: `/api`
- **文档地址**: http://localhost:8000/docs

## 接口列表

### 1. 健康检查

**接口**: `GET /api/health`

**描述**: 检查系统健康状态

**响应示例**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "api_keys_configured": {
    "dashscope": true,
    "government": false,
    "wenxin": false
  },
  "chromadb_status": "healthy (2 documents)"
}
```

---

### 2. 文化分析

**接口**: `POST /api/analyze`

**描述**: 分析乡村文化特色

**请求体**:
```json
{
  "village_info": {
    "name": "西递村",
    "location": "安徽省黄山市",
    "industry": "旅游、徽派建筑保护",
    "history": "明清古村落，以马头墙和木雕闻名",
    "custom_info": ""
  }
}
```

**响应示例**:
```json
{
  "status": "success",
  "message": "文化分析完成",
  "culture_analysis": "## 核心文化元素\n...",
  "data_sources": [
    "ChromaDB知识库",
    "政府开放数据平台",
    "通义千问AI分析"
  ],
  "timestamp": "2025-10-13T10:30:00"
}
```

---

### 3. 设计方案生成

**接口**: `POST /api/design`

**描述**: 生成墙绘设计方案

**请求体**:
```json
{
  "culture_analysis": "## 核心文化元素\n...",
  "user_preference": "希望更突出木雕元素"
}
```

**响应示例**:
```json
{
  "status": "success",
  "message": "设计方案生成完成",
  "design_options": "## 方案A：传统文化风格\n...",
  "num_options": 3,
  "timestamp": "2025-10-13T10:35:00"
}
```

---

### 4. 图像生成（异步）

**接口**: `POST /api/generate-image`

**描述**: 创建图像生成任务

**请求体**:
```json
{
  "design_option": "## 方案A：传统文化风格\n...",
  "style_preference": "traditional",
  "image_prompt": "可选的自定义Prompt"
}
```

**响应示例**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "progress": 0,
  "created_at": "2025-10-13T10:40:00",
  "updated_at": "2025-10-13T10:40:00"
}
```

---

### 5. 任务状态查询

**接口**: `GET /api/task/{task_id}`

**描述**: 查询异步任务状态

**路径参数**:
- `task_id`: 任务ID

**响应示例（处理中）**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 50,
  "result": null,
  "error": null,
  "created_at": "2025-10-13T10:40:00",
  "updated_at": "2025-10-13T10:40:30"
}
```

**响应示例（完成）**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "result": {
    "status": "success",
    "images": [
      {
        "url": "",
        "local_path": "./data/generated_images/generated_20251013_104100_0.png"
      }
    ],
    "prompt": "A beautiful Chinese village mural...",
    "style": "traditional",
    "is_mock": false
  },
  "error": null,
  "created_at": "2025-10-13T10:40:00",
  "updated_at": "2025-10-13T10:41:00"
}
```

---

### 6. 设计优化

**接口**: `POST /api/refine-design`

**描述**: 根据用户反馈优化设计方案

**请求体**:
```json
{
  "original_design": "## 方案A：传统文化风格\n...",
  "user_feedback": "希望马头墙的轮廓更明显"
}
```

**响应示例**:
```json
{
  "status": "success",
  "message": "设计方案优化完成",
  "design_options": "## 优化后的方案A\n...",
  "num_options": 1,
  "timestamp": "2025-10-13T10:45:00"
}
```

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 500 | 服务器内部错误 |

## 错误响应格式

```json
{
  "status": "error",
  "message": "错误描述",
  "timestamp": "2025-10-13T10:50:00"
}
```

## 使用示例

### Python

```python
import requests

# 文化分析
response = requests.post(
    "http://localhost:8000/api/analyze",
    json={
        "village_info": {
            "name": "西递村",
            "location": "安徽省黄山市",
            "industry": "旅游",
            "history": "明清古村落"
        }
    }
)

result = response.json()
print(result['culture_analysis'])
```

### JavaScript

```javascript
// 文化分析
fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    village_info: {
      name: '西递村',
      location: '安徽省黄山市',
      industry: '旅游',
      history: '明清古村落'
    }
  })
})
.then(response => response.json())
.then(data => console.log(data.culture_analysis));
```

### cURL

```bash
# 文化分析
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "village_info": {
      "name": "西递村",
      "location": "安徽省黄山市",
      "industry": "旅游",
      "history": "明清古村落"
    }
  }'
```

