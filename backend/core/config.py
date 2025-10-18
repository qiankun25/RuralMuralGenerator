"""
配置管理模块
使用 pydantic-settings 管理环境变量和应用配置
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ==================== LLM API配置 ====================
    dashscope_api_key: str = Field(
        default="",
        description="阿里云通义千问API密钥"
    )
    
    wenxin_api_key: Optional[str] = Field(
        default=None,
        description="文心一言API密钥（备用）"
    )

    
    
    # ==================== 数据库配置 ====================
    chromadb_path: str = Field(
        default="./data/chromadb",
        description="ChromaDB存储路径"
    )
    
    chromadb_collection_villages: str = Field(
        default="villages_knowledge",
        description="村落知识库集合名称"
    )
    
    chromadb_collection_designs: str = Field(
        default="design_cases",
        description="设计案例集合名称"
    )
    
    sqlite_db_path: str = Field(
        default="./data/app.db",
        description="SQLite数据库路径"
    )
    
    # ==================== 应用配置 ====================
    backend_host: str = Field(
        default="0.0.0.0",
        description="后端服务主机"
    )
    
    backend_port: int = Field(
        default=8000,
        description="后端服务端口"
    )
    
    backend_reload: bool = Field(
        default=True,
        description="开发模式自动重载"
    )
    
    frontend_port: int = Field(
        default=8501,
        description="前端服务端口"
    )
    
    api_base_url: str = Field(
        default="http://localhost:8000",
        description="后端API基础URL"
    )
    
    # ==================== 日志配置 ====================
    log_level: str = Field(
        default="INFO",
        description="日志级别"
    )
    
    # ==================== 缓存配置 ====================
    redis_url: Optional[str] = Field(
        default=None,
        description="Redis URL（可选）"
    )
    
    enable_cache: bool = Field(
        default=True,
        description="是否启用缓存"
    )
    
    cache_ttl: int = Field(
        default=3600,
        description="缓存过期时间（秒）"
    )
    
    # ==================== 图像生成配置 ====================
    image_output_dir: str = Field(
        default="./data/generated_images",
        description="生成图像输出目录"
    )
    
    max_image_size: int = Field(
        default=2048,
        description="最大图像尺寸"
    )
    
    default_image_style: str = Field(
        default="<chinese-painting>",
        description="默认图像风格"
    )
    
    image_generation_timeout: int = Field(
        default=120,
        description="图像生成超时时间（秒）"
    )
    
    # ==================== 敏感词检测 ====================
    sensitive_words_path: str = Field(
        default="./data/sensitive_words.txt",
        description="敏感词库路径"
    )
    
    enable_content_review: bool = Field(
        default=True,
        description="是否启用内容审核"
    )
    
    # ==================== LLM模型配置 ====================
    llm_model_name: str = Field(
        default="qwen-flash",
        description="LLM模型名称"
    )
    
    llm_temperature: float = Field(
        default=0.7,
        description="LLM温度参数"
    )
    
    llm_max_tokens: int = Field(
        default=2000,
        description="LLM最大token数"
    )
    
    # ==================== Embedding模型配置 ====================
    embedding_model_name: str = Field(
        default="text-embedding-v2",
        description="Embedding模型名称"
    )
    
    # ==================== 政府API配置 ====================
    government_api_timeout: int = Field(
        default=30,
        description="政府API超时时间（秒）"
    )
    
    government_api_retry: int = Field(
        default=3,
        description="政府API重试次数"
    )
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.chromadb_path,
            self.image_output_dir,
            os.path.dirname(self.sqlite_db_path),
            "./logs",
            "./data/knowledge/villages",
            "./data/knowledge/design_cases",
            "./data/mock_images"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def validate_api_keys(self) -> dict:
        """验证API密钥配置"""
        validation_result = {
            "dashscope": bool(self.dashscope_api_key and self.dashscope_api_key != ""),
            "wenxin": bool(self.wenxin_api_key)
        }
        return validation_result


# 创建全局配置实例
settings = Settings()

# 确保目录存在
settings.ensure_directories()


if __name__ == "__main__":
    # 测试配置
    print("=== 配置信息 ===")
    print(f"后端地址: {settings.backend_host}:{settings.backend_port}")
    print(f"ChromaDB路径: {settings.chromadb_path}")
    print(f"图像输出目录: {settings.image_output_dir}")
    
    print("\n=== API密钥验证 ===")
    validation = settings.validate_api_keys()
    for api, is_valid in validation.items():
        status = "✅" if is_valid else "❌"
        print(f"{status} {api}: {'已配置' if is_valid else '未配置'}")

