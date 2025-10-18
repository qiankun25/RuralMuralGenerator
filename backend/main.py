"""
FastAPI主应用
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from core.config import settings
from api.routes import router
from services import chromadb_service
from fastapi.staticfiles import StaticFiles


# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level
)
logger.add(
    "./logs/app.log",
    rotation="500 MB",
    retention="10 days",
    level=settings.log_level
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ========启动逻辑========
    logger.info("=" * 60)
    logger.info("乡村墙绘AI生成系统 - 后端服务启动")
    logger.info("=" * 60)

    # 初始化ChromaDB
    try:
        logger.info("初始化ChromaDB...")
        chromadb_service.initialize()
        logger.info("✅ ChromaDB初始化成功")
    except Exception as e:
        logger.error(f"❌ ChromaDB初始化失败: {e}")
    
    # 验证API密钥
    logger.info("验证API密钥配置...")
    api_keys_status = settings.validate_api_keys()
    for api, is_valid in api_keys_status.items():
        status = "✅" if is_valid else "❌"
        logger.info(f"{status} {api}: {'已配置' if is_valid else '未配置'}")
    
    logger.info("=" * 60)
    logger.info(f"后端服务已启动: http://{settings.backend_host}:{settings.backend_port}")
    logger.info(f"API文档: http://{settings.backend_host}:{settings.backend_port}/docs")
    logger.info("=" * 60)

    # =========应用运行中========
    yield

    # =========关闭逻辑=========
    logger.info("后端服务正在关闭...")



# 创建FastAPI应用
app = FastAPI(
    title="乡村墙绘AI生成系统",
    description="基于多智能体协作和RAG技术的乡村墙绘个性化设计系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# 配置CORS（允许Streamlit前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO:生产环境后配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(router, prefix="/api", tags=["API"])

# 挂载静态文件目录，暴露生成的图片
try:
    app.mount("/media", StaticFiles(directory=settings.image_output_dir), name="media")
    logger.info(f"✅ 静态文件已挂载: /media -> {settings.image_output_dir}")
except Exception as e:
    logger.error(f"静态文件挂载失败: {e}")


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "乡村墙绘AI生成系统 - 后端API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.backend_reload,
        log_level=settings.log_level.lower()
    )

