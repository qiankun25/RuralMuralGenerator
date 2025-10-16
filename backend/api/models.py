"""
API请求和响应模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# ==================== 请求模型 ====================

class VillageInfo(BaseModel):
    """村落信息"""
    name: str = Field(..., description="村落名称")
    location: str = Field(..., description="地理位置")
    industry: Optional[str] = Field(None, description="特色产业")
    history: Optional[str] = Field(None, description="历史故事")
    custom_info: Optional[str] = Field(None, description="其他自定义信息")


class AnalyzeRequest(BaseModel):
    """文化分析请求"""
    village_info: VillageInfo = Field(..., description="村落信息")


class DesignRequest(BaseModel):
    """设计方案生成请求"""
    culture_analysis: str = Field(..., description="文化分析报告")
    user_preference: Optional[str] = Field(None, description="用户偏好")


class ImageGenerationRequest(BaseModel):
    """图像生成请求"""
    design_option: str = Field(..., description="选定的设计方案")
    style_preference: str = Field(default="traditional", description="风格偏好")
    image_prompt: Optional[str] = Field(None, description="自定义图像Prompt")


class RefineDesignRequest(BaseModel):
    """设计优化请求"""
    original_design: str = Field(..., description="原始设计方案")
    user_feedback: str = Field(..., description="用户反馈")


# ==================== 响应模型 ====================

class BaseResponse(BaseModel):
    """基础响应"""
    status: str = Field(..., description="状态: success/error")
    message: Optional[str] = Field(None, description="消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class AnalyzeResponse(BaseResponse):
    """文化分析响应"""
    culture_analysis: Optional[str] = Field(None, description="文化分析报告")
    data_sources: Optional[List[str]] = Field(None, description="数据来源")


class DesignResponse(BaseResponse):
    """设计方案响应"""
    design_options: Optional[str] = Field(None, description="设计方案（Markdown格式）")
    num_options: Optional[int] = Field(None, description="方案数量")


class ImageInfo(BaseModel):
    """图像信息"""
    url: Optional[str] = Field(None, description="图像URL")
    local_path: Optional[str] = Field(None, description="本地路径")


class ImageGenerationResponse(BaseResponse):
    """图像生成响应"""
    images: Optional[List[ImageInfo]] = Field(None, description="生成的图像列表")
    prompt: Optional[str] = Field(None, description="使用的Prompt")
    style: Optional[str] = Field(None, description="图像风格")
    is_mock: Optional[bool] = Field(False, description="是否为Mock图像")


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态: pending/processing/completed/failed")
    progress: int = Field(default=0, description="进度百分比")
    result: Optional[Dict] = Field(None, description="任务结果")
    error: Optional[str] = Field(None, description="错误信息")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


# ==================== 其他模型 ====================

class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(default="healthy", description="服务状态")
    version: str = Field(default="1.0.0", description="版本号")
    api_keys_configured: Dict[str, bool] = Field(..., description="API密钥配置状态")
    chromadb_status: str = Field(..., description="ChromaDB状态")

