# 🏡 乡村墙绘AI生成系统

基于多智能体协作（CrewAI + LangChain）和RAG技术的乡村墙绘个性化设计系统

## 📋 项目简介

本项目是一个AI应用，旨在解决乡村墙绘同质化问题，通过多智能体协作为每个乡村生成独特的文化墙绘设计。

### 核心特性

- 🤖 **多智能体协作**：CrewAI编排 + LangChain实现的4个专业智能体
- 📚 **RAG技术**：基于ChromaDB的向量知识库，实现语义检索
- 🎨 **个性化设计**：深度分析乡村文化，生成定制化墙绘方案
- 🖼️ **AI图像生成**：集成通义万相API，生成高质量墙绘图像
- 🌐 **前后端分离**：FastAPI后端 + Streamlit前端
- 📊 **政府数据集成**：接入政府开放数据平台API

## 🏗️ 系统架构

```
前端层 (Streamlit)
    ↓ HTTP REST API
后端层 (FastAPI)
    ↓
业务逻辑层 (CrewAI + LangChain)
    ├── 文化分析Agent (LangChain)
    ├── 创意设计Agent (LangChain)
    ├── 图像生成Agent
    └── 审核优化Agent
    ↓
数据层 (ChromaDB + SQLite)
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入以下API密钥：
# - DASHSCOPE_API_KEY（通义千问/万相）
# - GOVERNMENT_API_KEY（政府开放数据平台）
```

### 3. 初始化知识库

```bash
# 初始化ChromaDB向量数据库
python scripts/init_chromadb.py
```

### 4. 启动服务

```bash
# 启动后端（FastAPI）
cd backend
uvicorn main:app --reload --port 8000

# 新开终端，启动前端（Streamlit）
cd frontend
streamlit run app.py
```

### 5. 访问应用

- 前端界面：http://localhost:8501
- 后端API文档：http://localhost:8000/docs

## 📁 项目结构

```
RuralMuralGenerator/
├── frontend/              # Streamlit前端
│   └── app.py            # 单页面应用
├── backend/              # FastAPI后端
│   ├── main.py          # 主应用
│   ├── api/             # API路由
│   ├── agents/          # CrewAI + LangChain智能体
│   ├── tools/           # LangChain工具
│   ├── services/        # 业务服务
│   └── core/            # 核心配置
├── data/                # 数据目录
│   ├── chromadb/        # 向量数据库
│   ├── knowledge/       # 知识库原始数据
│   └── generated_images/# 生成的图像
├── scripts/             # 工具脚本
└── tests/               # 测试
```

## 🤖 智能体说明

### 1. 文化分析Agent
- **技术**：LangChain Agent + ChromaDB + 政府API
- **功能**：深度分析乡村文化特色，生成结构化报告

### 2. 创意设计Agent
- **技术**：LangChain Chain + Prompt Engineering
- **功能**：基于文化分析生成3个墙绘设计方案

### 3. 图像生成Agent
- **技术**：通义万相API
- **功能**：根据设计方案生成高质量墙绘图像

### 4. 经理路由Agent
- **技术**：CrewAI 
- **功能**：根据用户输入和智能体输出，进行路由和任务分配

## 📚 技术栈

- **前端**：Streamlit
- **后端**：FastAPI
- **智能体编排**：CrewAI
- **智能体实现**：LangChain
- **向量数据库**：ChromaDB
- **LLM**：阿里云通义千问
- **图像生成**：阿里云通义万相

## 📖 使用说明

详细使用说明请参考：[使用文档](docs/usage.md)

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_agents.py

# 查看测试覆盖率
pytest --cov=backend tests/
```


## 🔗 相关链接

- **通义千问API**：https://dashscope.aliyun.com/
- **ChromaDB文档**：https://docs.trychroma.com/
- **LangChain文档**：https://python.langchain.com/
- **CrewAI文档**：https://docs.crewai.com/
- **FastAPI文档**：https://fastapi.tiangolo.com/
- **Streamlit文档**：https://docs.streamlit.io/




