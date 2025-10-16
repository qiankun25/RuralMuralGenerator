# 项目部署指南

## 环境要求

- Python 3.9+
- pip
- 虚拟环境工具（推荐使用venv）

## 快速开始

### 1. 克隆项目

```bash
cd RuralMuralGenerator
```

### 2. 激活虚拟环境

**Windows:**
```bash
maral-generator-env\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
copy .env.example .env  # Windows
# 或
cp .env.example .env    # Linux/Mac

# 编辑.env文件，填入API密钥
notepad .env  # Windows
# 或
nano .env     # Linux/Mac
```
#### 百度千帆配置示例
from openai import OpenAI

client = OpenAI(
    api_key="bce-v3/ALTAK-KZke********/f1d6ee*************",  # 千帆bearer token
    base_url="https://qianfan.baidubce.com/v2",  # 千帆域名
    default_headers={"appid": "app-xxxxxx"}   # 用户在千帆上的appid，非必传
)

completion = client.chat.completions.create(
    model="ernie-4.0-turbo-8k", # 预置服务请查看模型列表，定制服务请填入API地址
    messages=[{'role': 'system', 'content': 'You are a helpful assistant.'},
              {'role': 'user', 'content': 'Hello！'}]
)

print(completion.choices[0].message)
**必需配置项：**
- `DASHSCOPE_API_KEY`: 阿里云通义千问/万相API密钥
  - 申请地址：https://dashscope.aliyun.com/
  - 注册后在控制台获取API Key


### 5. 初始化ChromaDB知识库

```bash
python scripts/init_chromadb.py
```

按照提示操作：
- 首次运行选择 `y` 重置数据库
- 等待知识库初始化完成
- 可选择测试检索功能

### 6. 启动后端服务

**方式1：使用脚本（Windows）**
```bash
scripts\start_backend.bat
```

**方式2：手动启动**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

启动成功后，访问：
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/health

### 7. 启动前端服务

**新开一个终端窗口**

**方式1：使用脚本（Windows）**
```bash
scripts\start_frontend.bat
```

**方式2：手动启动**
```bash
cd frontend
streamlit run app.py
```

启动成功后，浏览器会自动打开：http://localhost:8501

## 验证安装

### 1. 检查后端健康状态

访问：http://localhost:8000/api/health

应该看到类似输出：
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

### 2. 测试前端连接

在Streamlit界面的侧边栏，应该看到：
- ✅ 后端服务正常

### 3. 测试完整流程

1. 输入测试数据：
   - 乡村名称：西递村
   - 地理位置：安徽省黄山市
   - 历史故事：明清古村落，以马头墙和木雕闻名

2. 点击"开始生成"

3. 等待文化分析完成

4. 查看设计方案

5. 选择一个方案生成图像

## 常见问题

### Q1: 提示"后端服务未连接"

**解决方案：**
1. 确认后端服务已启动（检查终端是否有报错）
2. 检查端口8000是否被占用
3. 检查防火墙设置

### Q2: ChromaDB初始化失败

**解决方案：**
1. 确认已安装所有依赖：`pip install -r requirements.txt`
2. 删除 `data/chromadb` 目录后重新初始化
3. 检查Python版本是否为3.9+

### Q3: 图像生成失败或返回Mock图像

**原因：**
- 未配置通义万相API密钥
- API密钥额度不足
- 网络连接问题

**解决方案：**
1. 检查.env文件中的`DASHSCOPE_API_KEY`是否正确
2. 访问阿里云控制台检查API额度
3. 检查网络连接

### Q4: LLM调用失败

**解决方案：**
1. 检查API密钥是否正确
2. 检查网络连接
3. 查看后端日志（logs/app.log）获取详细错误信息

### Q5: 依赖安装失败

**解决方案：**
1. 升级pip：`pip install --upgrade pip`
2. 使用国内镜像源：
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

## 开发模式

### 查看日志

后端日志位置：`logs/app.log`

实时查看日志：
```bash
# Windows
type logs\app.log

# Linux/Mac
tail -f logs/app.log
```

### 重置数据库

```bash
python scripts/init_chromadb.py
# 选择 y 重置数据库
```

### 测试API

使用Swagger UI：http://localhost:8000/docs

或使用curl：
```bash
curl http://localhost:8000/api/health
```

## 生产部署

### 使用Docker（推荐）

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 手动部署

1. 使用gunicorn替代uvicorn：
```bash
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. 使用nginx反向代理

3. 配置HTTPS证书

4. 设置环境变量：
```bash
export BACKEND_RELOAD=false
export LOG_LEVEL=WARNING
```

## 性能优化

### 1. 启用Redis缓存

安装Redis并配置：
```bash
# .env
REDIS_URL=redis://localhost:6379/0
ENABLE_CACHE=true
```

### 2. 调整LLM参数

编辑 `.env`:
```bash
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
```


