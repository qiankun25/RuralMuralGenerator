# 🚀 快速启动指南

## 5分钟快速体验

### 步骤1：安装依赖（2分钟）

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
venv\Scripts\activate  # Windows
# 或
source venv/bin/activate  # Linux/Mac

# 3. 安装依赖
pip install -r requirements.txt
```

### 步骤2：配置API密钥（1分钟）

```bash
# 1. 复制环境变量模板
copy .env.example .env  # Windows
# 或
cp .env.example .env    # Linux/Mac

# 2. 编辑.env文件
notepad .env  # Windows
# 或
nano .env     # Linux/Mac
```

**最少配置（必需）：**
```bash
DASHSCOPE_API_KEY=your_api_key_here
```

> 💡 **获取API密钥**：访问 https://dashscope.aliyun.com/ 注册并获取免费API Key

### 步骤3：初始化知识库（1分钟）

```bash
python scripts/init_chromadb.py
```

按提示操作：
- 输入 `y` 重置数据库
- 等待初始化完成
- 输入 `n` 跳过测试

### 步骤4：启动服务（1分钟）

**终端1 - 启动后端：**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**终端2 - 启动前端：**
```bash
cd frontend
streamlit run app.py
```

### 步骤5：开始使用

浏览器自动打开 http://localhost:8501

**测试数据：**
- 乡村名称：`西递村`
- 地理位置：`安徽省黄山市`
- 特色产业：`旅游、徽派建筑保护`
- 历史故事：`明清古村落，以马头墙和木雕闻名，是世界文化遗产`

点击"开始生成"，等待AI完成分析和设计！

---

## 常见问题快速解决

### ❌ 后端服务未连接

**检查清单：**
1. ✅ 后端是否启动？（检查终端1）
2. ✅ 端口8000是否被占用？
3. ✅ 虚拟环境是否激活？

**解决方案：**
```bash
# 重启后端
cd backend
python -m uvicorn main:app --reload --port 8000
```

### ❌ ChromaDB初始化失败

**解决方案：**
```bash
# 删除旧数据
rmdir /s data\chromadb  # Windows
# 或
rm -rf data/chromadb    # Linux/Mac

# 重新初始化
python scripts/init_chromadb.py
```

### ❌ 图像生成返回Mock图像

**原因：** 未配置通义万相API密钥

**解决方案：**
1. 检查 `.env` 文件中的 `DASHSCOPE_API_KEY`
2. 确保API密钥有效且有额度
3. 重启后端服务

### ❌ 依赖安装失败

**解决方案：**
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 项目结构速览

```
RuralMuralGenerator/
├── backend/              # FastAPI后端
│   ├── main.py          # 主应用入口
│   ├── agents/          # CrewAI + LangChain智能体
│   ├── services/        # 业务服务（ChromaDB、LLM、图像生成）
│   ├── tools/           # LangChain工具
│   └── api/             # API路由
├── frontend/            # Streamlit前端
│   └── app.py          # 单页面应用
├── data/               # 数据目录
│   ├── chromadb/       # 向量数据库
│   └── knowledge/      # 知识库原始数据
├── scripts/            # 工具脚本
│   └── init_chromadb.py # 初始化脚本
└── docs/               # 文档
```

---

## 核心功能演示

### 1️⃣ 文化分析（AI + RAG）

系统会：
- 🔍 从ChromaDB检索相关村落知识
- 🌐 查询政府开放数据平台
- 🤖 使用通义千问深度分析
- 📊 生成结构化文化分析报告

### 2️⃣ 创意设计（多方案生成）

系统会：
- 🎨 生成3个不同风格的设计方案
- 🎭 传统文化风格 / 现代简约风格 / 文化叙事风格
- 🖌️ 包含色彩搭配、构图建议、文化寓意
- 📝 提供英文图像生成Prompt

### 3️⃣ 图像生成（AI绘画）

系统会：
- 🖼️ 调用通义万相API生成高质量图像
- 🎨 支持多种艺术风格
- 💾 自动保存到本地
- 📥 支持下载

---

## 下一步

- 📖 阅读完整文档：[docs/SETUP.md](docs/SETUP.md)
- 🔧 查看API文档：http://localhost:8000/docs
- 🎓 了解技术架构：[README.md](README.md)

---

## 技术支持

遇到问题？
1. 查看日志：`logs/app.log`
2. 检查健康状态：http://localhost:8000/api/health
3. 查看详细文档：[docs/SETUP.md](docs/SETUP.md)

---

**祝您使用愉快！** 🎉

