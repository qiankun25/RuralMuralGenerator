# 🔄 后端处理逻辑详解

## 📋 目录
1. [完整工作流](#完整工作流)
2. [各阶段详细处理](#各阶段详细处理)
3. [关键算法和技术](#关键算法和技术)
4. [错误处理和降级](#错误处理和降级)

---

## 完整工作流

### 用户交互流程

```
┌─────────────────────────────────────────────────────────────┐
│ 步骤1：用户输入乡村信息                                      │
│ (名称、位置、产业、历史)                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 步骤2：文化分析 (同步)                                       │
│ ├─ 检索知识库 (ChromaDB)                                    │
│ ├─ 查询政府数据                                             │
│ └─ LLM深度分析                                              │
│ 输出：文化分析报告                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 步骤3：设计方案生成 (同步)                                   │
│ ├─ 检索设计案例 (ChromaDB)                                  │
│ ├─ LLM生成3个方案                                           │
│ └─ 敏感词检测                                               │
│ 输出：3个设计方案                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 步骤4：用户选择方案                                          │
│ (前端展示3个方案，用户选择)                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 步骤5：图像生成 (异步)                                       │
│ ├─ 提取/优化Prompt                                          │
│ ├─ 调用图像生成API                                          │
│ └─ 下载和存储图像                                           │
│ 输出：生成的墙绘图像                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 步骤6：结果展示和下载                                        │
│ (前端展示图像和完整报告)                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 各阶段详细处理

### 阶段1：文化分析处理

#### 1.1 知识库检索

**输入**：村落信息（名称、位置、产业、历史）

**处理流程**：
```python
# 1. 构建检索查询
query = f"{village_name} {location} {industry}"

# 2. 向量化查询（使用Embedding模型）
# 模型：paraphrase-multilingual-MiniLM-L12-v2

# 3. 在ChromaDB中进行语义搜索
results = chromadb_service.search_villages(query, n_results=3)

# 4. 返回相关度最高的3个文档
# 相关度计算：1 - cosine_distance
```

**输出**：
```
【知识库检索结果】

参考资料1：
相关度：0.85
内容：西递村位于安徽省黄山市，是典型的徽派建筑古村落...

参考资料2：
相关度：0.78
内容：徽派建筑以马头墙、青砖黛瓦、精美木雕闻名...
```

#### 1.2 政府数据查询

**输入**：村落名称

**处理流程**：
```python
# 1. 调用政府开放数据API
result = government_service.query_village_data_sync(village_name)

# 2. 如果API不可用，返回Mock数据
# 支持缓存机制

# 3. 提取关键信息
# - 行政区划
# - 特色标签
# - 文化遗产信息
# - 建筑特色
# - 历史沿革
```

**输出**：
```
【政府开放数据】

村落名称：西递村
行政区划：安徽省 黄山市 黟县
特色标签：徽派建筑、古村落、文化遗产
文化遗产信息：
- 建筑特色：马头墙、青砖黛瓦
- 历史沿革：明清古村落
- 文化内涵：徽商文化、传统工艺
```

#### 1.3 LLM深度分析

**输入**：村落信息 + 知识库检索结果 + 政府数据

**处理流程**：
```python
# 1. 构建System Prompt
system_prompt = """你是一位资深的乡村文化研究专家，
擅长分析中国传统村落的文化特色。"""

# 2. 构建User Prompt
user_prompt = f"""请分析以下乡村的文化特色：
【村落基本信息】
- 名称：{name}
- 地理位置：{location}
...
【参考知识库】
{knowledge_context}
...
"""

# 3. 调用LLM（通义千问）
# 参数：
# - model: qwen-plus
# - temperature: 0.7（创意性）
# - max_tokens: 2000

# 4. LLM返回结构化分析报告
```

**输出**（Markdown格式）：
```markdown
## 核心文化元素
- 徽派建筑：马头墙、青砖黛瓦
- 徽商文化：诚信经营、耕读传家
- 传统工艺：木雕、石雕、砖雕

## 推荐色彩方案
- 青灰色 #2C3E50（主色调）
- 白墙色 #ECF0F1（辅助色）
- 朱红色 #E74C3C（点缀色）

## 推荐文化符号
- 马头墙图案
- 徽派窗花
- 传统纹样
...

## 设计建议
...

## 文化故事线索
...
```

---

### 阶段2：设计方案生成处理

#### 2.1 设计案例检索

**输入**：文化分析报告

**处理流程**：
```python
# 1. 从文化分析中提取关键词
query = culture_analysis[:200]  # 取前200字符

# 2. 向量化查询

# 3. 在设计案例库中搜索
results = chromadb_service.search_design_cases(query, n_results=2)

# 4. 返回相关度最高的2个设计案例
```

**输出**：
```
【设计案例参考】

案例1：
相关度：0.82
内容：某村落墙绘设计案例，采用传统风格...

案例2：
相关度：0.75
内容：另一个村落的现代简约风格设计...
```

#### 2.2 LLM生成设计方案

**输入**：文化分析报告 + 设计案例 + 用户偏好

**处理流程**：
```python
# 1. 构建System Prompt
system_prompt = """你是一位经验丰富的墙绘艺术设计师，
擅长将文化元素转化为视觉设计方案。"""

# 2. 构建User Prompt
user_prompt = f"""基于以下文化分析报告，请生成3个不同风格的墙绘设计方案：

【文化分析报告】
{culture_analysis}

【用户偏好】
{user_preference}

请为每个方案提供：
- 设计主题
- 核心元素
- 色彩搭配
- 构图建议
- 文化寓意
- 图像生成Prompt（英文）
"""

# 3. 调用LLM
# 参数：
# - temperature: 0.8（更有创意）
# - max_tokens: 2500

# 4. LLM返回3个设计方案
```

**输出**（Markdown格式）：
```markdown
## 方案A：传统文化风格
- **设计主题**：徽派建筑与文化传承
- **核心元素**：马头墙、青砖黛瓦、传统纹样
- **色彩搭配**：青灰色 + 白色 + 朱红色
- **构图建议**：左右对称，中心突出
- **文化寓意**：展现徽派建筑的历史底蕴
- **图像生成Prompt**：A traditional Chinese mural painting...

## 方案B：现代简约风格
...

## 方案C：文化叙事风格
...
```

#### 2.3 敏感词检测

**输入**：生成的设计方案

**处理流程**：
```python
# 1. 加载敏感词库
# 路径：./data/sensitive_words.txt

# 2. 逐行检查设计方案
result = checker.check_text(design_options)

# 3. 返回检测结果
# - is_safe: bool
# - found_words: List[str]

# 4. 如果包含敏感词，记录警告（不阻止）
```

---

### 阶段3：图像生成处理

#### 3.1 Prompt提取和优化

**输入**：选定的设计方案

**处理流程**：
```python
# 1. 从设计方案中提取图像生成Prompt
# 通常在"图像生成Prompt"字段中

# 2. 使用LLM优化Prompt
system_prompt = """你是一位AI图像生成专家，
擅长将设计描述转化为高质量的图像生成Prompt。"""

user_prompt = f"""请将以下墙绘设计描述转化为详细的英文图像生成Prompt：

{design_description}

要求：
1. 使用英文
2. 包含风格、主体、色彩、构图等关键信息
3. 长度控制在50-100个英文单词
4. 适合用于Stable Diffusion或通义万相
5. 添加质量提升关键词（high quality, detailed, artistic等）
"""

# 3. LLM返回优化后的Prompt
```

**输出**：
```
A traditional Chinese mural painting featuring Hui-style architecture 
with white walls, black tiles, and horse-head walls, artistic, detailed, 
high quality, vibrant colors, cultural symbols, masterpiece
```

#### 3.2 图像生成

**输入**：优化后的Prompt + 风格偏好

**处理流程**：
```python
# 1. 根据风格偏好选择通义万相的style参数
style_mapping = {
    "traditional": "<chinese-painting>",    # 中国画风格
    "modern": "<flat-illustration>",        # 扁平插画
    "narrative": "<watercolor>"             # 水彩风格
}

# 2. 增强Prompt
enhanced_prompt = f"{prompt}, high quality, detailed, artistic, mural painting, vibrant colors"

# 3. 添加负面提示词
negative_prompt = "low quality, blurry, distorted, ugly, bad anatomy, watermark, text"

# 4. 调用通义万相API
response = ImageSynthesis.call(
    model='wanx-v1',
    prompt=enhanced_prompt,
    negative_prompt=negative_prompt,
    style=style,
    size="1024*1024",
    n=1
)

# 5. 处理响应
if response.status_code == HTTPStatus.OK:
    image_url = response.output.results[0].url
    # 下载图像到本地
    local_path = _download_image(image_url)
else:
    # 返回Mock图像（降级方案）
    return _get_mock_image()
```

#### 3.3 异步任务管理

**任务状态流转**：
```
pending (0%)
    ↓
processing (10%)
    ↓
processing (30%) - 提取Prompt
    ↓
processing (90%) - 生成图像
    ↓
completed (100%) 或 failed
```

**任务存储结构**：
```python
tasks_storage[task_id] = {
    "task_id": "uuid",
    "status": "pending|processing|completed|failed",
    "progress": 0-100,
    "result": {...},
    "error": None,
    "created_at": datetime,
    "updated_at": datetime
}
```

---

## 关键算法和技术

### 1. 向量检索（RAG）

**技术**：ChromaDB + Embedding

**流程**：
```
用户查询
    ↓
使用Embedding模型向量化
    ↓
计算与知识库文档的相似度
    ↓
返回相关度最高的K个文档
    ↓
作为LLM的上下文
```

**相关度计算**：
```
相关度 = 1 - cosine_distance(query_embedding, doc_embedding)
范围：0-1，越接近1越相关
```

### 2. LLM提示工程

**System Prompt**：定义Agent的角色和能力
**User Prompt**：包含具体任务和上下文
**Temperature**：控制创意性（0.5-0.8）
**Max Tokens**：控制输出长度

### 3. 异步处理

**使用FastAPI的BackgroundTasks**：
```python
background_tasks.add_task(
    _generate_image_task,
    task_id,
    design_option,
    style_preference,
    image_prompt
)
```

**前端轮询**：
```javascript
// 每2秒查询一次任务状态
GET /api/task/{task_id}
```

---

## 错误处理和降级

### 1. API调用失败

**处理策略**：
```python
try:
    result = llm_service.generate_text(prompt)
except Exception as e:
    logger.error(f"LLM调用失败: {e}")
    # 返回默认值或Mock数据
    return default_response
```

### 2. 图像生成失败

**降级方案**：
```python
if api_key_not_configured or api_call_failed:
    # 返回Mock图像
    return _get_mock_image()
```

### 3. 知识库为空

**处理**：
```python
if not results["documents"]:
    return "未找到相关知识库信息"
    # LLM仍可基于通用知识进行分析
```

### 4. 敏感词检测

**处理**：
```python
if not result["is_safe"]:
    logger.warning(f"包含敏感词: {result['found_words']}")
    # 仅记录警告，不阻止流程
```

---

## 性能优化

### 1. 缓存机制

- 政府API数据缓存
- ChromaDB向量缓存
- 可选Redis缓存

### 2. 异步处理

- 图像生成异步执行
- 不阻塞主线程

### 3. 批量操作

- 批量添加知识库文档
- 批量检索

---

## 总结

后端处理逻辑采用**分阶段、分层次**的设计：

1. **文化分析阶段**：多源数据融合 + LLM分析
2. **设计生成阶段**：案例参考 + LLM创意 + 内容审核
3. **图像生成阶段**：Prompt优化 + API调用 + 异步处理

整个流程通过**RAG技术**增强LLM的知识库，通过**多Agent协作**实现复杂任务的分解和执行。

