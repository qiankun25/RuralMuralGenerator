"""
图像生成服务
封装通义万相API调用
"""

from typing import Optional, Dict
import logging
logger = logging.getLogger(__name__)

try:
    import dashscope
except ImportError:
    logger.warning("DashScope未安装，请运行: pip install dashscope")
    dashscope = None
from dashscope import ImageSynthesis
from http import HTTPStatus
import os
import requests
from datetime import datetime

from core.config import settings


class ImageGenerationService:
    """图像生成服务类"""
    
    def __init__(self):
        """初始化图像生成服务"""
        self.api_key = settings.dashscope_api_key
        self.output_dir = settings.image_output_dir
        self.default_style = settings.default_image_style
        self.timeout = settings.image_generation_timeout
        
        # 设置API Key
        if self.api_key:
            dashscope.api_key = self.api_key
        else:
            logger.warning("未配置DASHSCOPE_API_KEY，图像生成功能将不可用")
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        style: Optional[str] = None,
        size: str = "1024*1024",
        n: int = 1
    ) -> Dict:
        """
        生成图像
        
        Args:
            prompt: 图像描述（英文）
            negative_prompt: 负面提示词（可选）
            style: 图像风格（可选）
            size: 图像尺寸，支持 "1024*1024", "720*1280", "1280*720"
            n: 生成图像数量（1-4）
            
        Returns:
            生成结果字典，包含图像URL和本地路径
        """
        try:
            if not self.api_key:
                logger.warning("未配置API密钥，返回Mock图像")
                return self._get_mock_image()
            
            logger.info(f"开始生成图像，Prompt: {prompt[:50]}...")
            
            # 调用通义万相API
            response = ImageSynthesis.call(
                model='wanx-v1',
                prompt=prompt,
                negative_prompt=negative_prompt,
                style=style or self.default_style,
                size=size,
                n=n
            )
            
            if response.status_code == HTTPStatus.OK:
                results = []
                
                for i, result in enumerate(response.output.results):
                    image_url = result.url
                    
                    # 下载图像到本地
                    local_path = self._download_image(image_url, f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}")
                    
                    results.append({
                        "url": image_url,
                        "local_path": local_path
                    })
                
                logger.info(f"图像生成成功，共 {len(results)} 张")
                
                return {
                    "status": "success",
                    "images": results,
                    "prompt": prompt,
                    "style": style or self.default_style
                }
            else:
                error_msg = f"图像生成失败: {response.code} - {response.message}"
                logger.error(error_msg)
                
                # 返回Mock图像作为降级方案
                logger.info("使用Mock图像作为降级方案")
                return self._get_mock_image()
                
        except Exception as e:
            logger.error(f"图像生成异常: {e}")
            # 返回Mock图像
            return self._get_mock_image()
    
    def _download_image(self, url: str, filename: str) -> str:
        """
        下载图像到本地
        
        Args:
            url: 图像URL
            filename: 文件名（不含扩展名）
            
        Returns:
            本地文件路径
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 保存图像
            filepath = os.path.join(self.output_dir, f"{filename}.png")
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"图像已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"下载图像失败: {e}")
            return ""
    
    def _get_mock_image(self) -> Dict:
        """
        获取Mock图像（用于演示或API不可用时）
        
        Returns:
            Mock图像信息
        """
        mock_images_dir = "./data/mock_images"
        os.makedirs(mock_images_dir, exist_ok=True)
        
        # 检查是否有Mock图像
        mock_images = [f for f in os.listdir(mock_images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        
        if mock_images:
            mock_image_path = os.path.join(mock_images_dir, mock_images[0])
            logger.info(f"使用Mock图像: {mock_image_path}")
            
            return {
                "status": "mock",
                "images": [{
                    "url": "",
                    "local_path": mock_image_path
                }],
                "prompt": "Mock image for demonstration",
                "style": "mock"
            }
        else:
            logger.warning("未找到Mock图像")
            return {
                "status": "error",
                "images": [],
                "prompt": "",
                "style": "",
                "error": "未配置API密钥且无Mock图像"
            }
    
    def generate_mural_image(
        self,
        design_prompt: str,
        style_preference: str = "traditional"
    ) -> Dict:
        """
        生成墙绘图像（高级接口）
        
        Args:
            design_prompt: 设计描述（英文）
            style_preference: 风格偏好 (traditional/modern/narrative)
            
        Returns:
            生成结果
        """
        # 根据风格偏好选择通义万相的style参数
        style_mapping = {
            "traditional": "<chinese-painting>",  # 中国画风格
            "modern": "<flat-illustration>",      # 扁平插画风格
            "narrative": "<watercolor>"           # 水彩风格
        }
        
        style = style_mapping.get(style_preference, self.default_style)
        
        # 添加质量提升关键词
        enhanced_prompt = f"{design_prompt}, high quality, detailed, artistic, mural painting, vibrant colors"
        
        # 负面提示词
        negative_prompt = "low quality, blurry, distorted, ugly, bad anatomy, watermark, text"
        
        return self.generate_image(
            prompt=enhanced_prompt,
            negative_prompt=negative_prompt,
            style=style,
            size="1024*1024",
            n=1
        )


# 创建全局图像生成服务实例
image_service = ImageGenerationService()


if __name__ == "__main__":
    # 测试图像生成服务
    test_prompt = "A beautiful Chinese village mural painting featuring traditional architecture, mountains, and cultural symbols"
    
    try:
        result = image_service.generate_mural_image(test_prompt, style_preference="traditional")
        print(f"生成结果: {result}")
    except Exception as e:
        print(f"测试失败: {e}")

