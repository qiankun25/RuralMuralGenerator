"""
API路由
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from http import HTTPStatus
import logging
logger = logging.getLogger(__name__)
from typing import Dict
import uuid
from datetime import datetime

from api.models import (
    AnalyzeRequest, AnalyzeResponse,
    DesignRequest, DesignResponse,
    ImageGenerationRequest, ImageGenerationResponse,
    RefineDesignRequest, BaseResponse,
    TaskStatusResponse, HealthCheckResponse,
    ImageInfo
)
from agents import culture_analyst, creative_designer, image_generator, crew_manager
from services import chromadb_service
from core.config import settings


# 创建路由器
router = APIRouter()

# 任务存储（简化版，生产环境应使用Redis或数据库）
tasks_storage: Dict[str, Dict] = {}


# ==================== 健康检查 ====================

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """健康检查接口"""
    try:
        # 检查API密钥配置
        api_keys_status = settings.validate_api_keys()
        
        # 检查ChromaDB状态
        chromadb_status = "healthy"
        try:
            if chromadb_service.villages_collection:
                count = chromadb_service.villages_collection.count()
                chromadb_status = f"healthy ({count} documents)"
            else:
                chromadb_status = "not_initialized"
        except Exception as e:
            chromadb_status = f"error: {str(e)}"
        
        return HealthCheckResponse(
            status="healthy",
            version="1.0.0",
            api_keys_configured=api_keys_status,
            chromadb_status=chromadb_status
        )
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            version="1.0.0",
            api_keys_configured={},
            chromadb_status="error"
        )


# ==================== 文化分析 ====================

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_culture(request: AnalyzeRequest):
    """
    文化分析接口
    
    同步返回文化分析报告
    """
    try:
        logger.info(f"收到文化分析请求: {request.village_info.name}")
        
        # 调用文化分析智能体
        culture_analysis = culture_analyst.analyze(request.village_info.dict())
        
        return AnalyzeResponse(
            status="success",
            message="文化分析完成",
            culture_analysis=culture_analysis,
            data_sources=["ChromaDB知识库", "政府开放数据平台", "通义千问AI分析"]
        )
        
    except Exception as e:
        logger.error(f"文化分析失败: {e}")
        return AnalyzeResponse(
            status="error",
            message=f"文化分析失败: {str(e)}"
        )


# ==================== 设计方案生成 ====================

@router.post("/design", response_model=DesignResponse)
async def generate_design(request: DesignRequest):
    """
    设计方案生成接口
    
    同步返回设计方案
    """
    try:
        logger.info("收到设计方案生成请求")
        
        # 调用创意设计智能体
        design_options = creative_designer.generate_designs(
            culture_analysis=request.culture_analysis,
            user_preference=request.user_preference
        )
        
        return DesignResponse(
            status="success",
            message="设计方案生成完成",
            design_options=design_options,
            num_options=3
        )
        
    except Exception as e:
        logger.error(f"设计方案生成失败: {e}")
        return DesignResponse(
            status="error",
            message=f"设计方案生成失败: {str(e)}"
        )


# ==================== 图像生成 ====================

@router.post("/generate-image", response_model=TaskStatusResponse)
async def generate_image(request: ImageGenerationRequest, background_tasks: BackgroundTasks):
    """
    图像生成接口（异步）
    
    创建异步任务，返回任务ID
    """
    try:
        logger.info("收到图像生成请求")
        
        # 创建任务ID
        task_id = str(uuid.uuid4())
        
        # 初始化任务状态
        tasks_storage[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "progress": 0,
            "result": None,
            "error": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # 添加后台任务
        background_tasks.add_task(
            _generate_image_task,
            task_id,
            request.design_option,
            request.style_preference,
            request.image_prompt
        )
        
        return TaskStatusResponse(
            task_id=task_id,
            status="pending",
            progress=0,
            message="图像生成任务已创建"
        )
        
    except Exception as e:
        logger.error(f"创建图像生成任务失败: {e}")
        return TaskStatusResponse(
            task_id="",
            status="failed",
            progress=0,
            error=str(e)
        )


async def _generate_image_task(
    task_id: str,
    design_option: str,
    style_preference: str,
    custom_prompt: str = None
):
    """图像生成后台任务"""
    try:
        # 更新任务状态
        tasks_storage[task_id]["status"] = "processing"
        tasks_storage[task_id]["progress"] = 10
        tasks_storage[task_id]["updated_at"] = datetime.now()
        
        # 提取或使用自定义Prompt
        if custom_prompt:
            image_prompt = custom_prompt
        else:
            image_prompt = creative_designer.extract_image_prompt(design_option)
        
        tasks_storage[task_id]["progress"] = 30
        tasks_storage[task_id]["updated_at"] = datetime.now()
        
        # 生成图像
        result = image_generator.generate(
            image_prompt=image_prompt,
            style_preference=style_preference
        )
        
        tasks_storage[task_id]["progress"] = 90
        tasks_storage[task_id]["updated_at"] = datetime.now()
        
        # 保存结果
        if result["status"] == "success":
            tasks_storage[task_id]["status"] = "completed"
            tasks_storage[task_id]["progress"] = 100
            tasks_storage[task_id]["result"] = result
        else:
            tasks_storage[task_id]["status"] = "failed"
            tasks_storage[task_id]["error"] = result.get("error", "未知错误")
        
        tasks_storage[task_id]["updated_at"] = datetime.now()
        
    except Exception as e:
        logger.error(f"图像生成任务失败: {e}")
        tasks_storage[task_id]["status"] = "failed"
        tasks_storage[task_id]["error"] = str(e)
        tasks_storage[task_id]["updated_at"] = datetime.now()


# ==================== 任务状态查询 ====================

@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    查询任务状态
    """
    try:
        if task_id not in tasks_storage:
            return TaskStatusResponse(
                task_id=task_id,
                status="not_found",
                progress=0,
                error="任务不存在"
            )
        
        task = tasks_storage[task_id]
        
        return TaskStatusResponse(
            task_id=task["task_id"],
            status=task["status"],
            progress=task["progress"],
            result=task.get("result"),
            error=task.get("error"),
            created_at=task["created_at"],
            updated_at=task["updated_at"]
        )
        
    except Exception as e:
        logger.error(f"查询任务状态失败: {e}")
        return TaskStatusResponse(
            task_id=task_id,
            status="error",
            progress=0,
            error=str(e)
        )


# ==================== 设计优化 ====================

@router.post("/refine-design", response_model=DesignResponse)
async def refine_design(request: RefineDesignRequest):
    """
    设计优化接口
    
    根据用户反馈优化设计方案
    """
    try:
        logger.info("收到设计优化请求")
        
        # 调用创意设计智能体的优化方法
        refined_design = creative_designer.refine_design(
            original_design=request.original_design,
            user_feedback=request.user_feedback
        )
        
        return DesignResponse(
            status="success",
            message="设计方案优化完成",
            design_options=refined_design,
            num_options=1
        )
        
    except Exception as e:
        logger.error(f"设计优化失败: {e}")
        return DesignResponse(
            status="error",
            message=f"设计优化失败: {str(e)}"
        )

