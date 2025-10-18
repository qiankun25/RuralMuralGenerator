"""
图像生成智能体
封装图像生成服务
"""

from typing import Dict, Optional
from loguru import logger

from services import image_service
from core.config import settings


class ImageGeneratorAgent:
    """图像生成智能体"""
    
    def __init__(self):
        """初始化图像生成智能体"""
        pass
    
    def generate(
        self,
        image_prompt: str,
        style_preference: str = "traditional",
        size: str = "1024*1024"
    ) -> Dict:
        """
        生成墙绘图像
        
        Args:
            image_prompt: 图像生成Prompt（英文）
            style_preference: 风格偏好 (traditional/modern/narrative)
            size: 图像尺寸
            
        Returns:
            生成结果字典
        """
        try:
            logger.info(f"开始生成图像，风格: {style_preference}")
            
            # 调用图像生成服务
            result = image_service.generate_mural_image(
                design_prompt=image_prompt,
                style_preference=style_preference
            )
            
            if result["status"] in ["success", "mock"]:
                logger.info("图像生成成功")
                return {
                    "status": "success",
                    "images": result["images"],
                    "prompt": image_prompt,
                    "style": style_preference,
                    "is_mock": result["status"] == "mock"
                }
            else:
                logger.error("图像生成失败")
                return {
                    "status": "error",
                    "error": result.get("error", "未知错误")
                }
                
        except Exception as e:
            logger.error(f"图像生成异常: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def regenerate(
        self,
        original_prompt: str,
        adjustment: str,
        style_preference: str = "traditional"
    ) -> Dict:
        """
        根据调整要求重新生成图像
        
        Args:
            original_prompt: 原始Prompt
            adjustment: 调整要求
            style_preference: 风格偏好
            
        Returns:
            生成结果字典
        """
        try:
            logger.info(f"根据调整要求重新生成图像: {adjustment}")
            
            # 将调整要求融入Prompt
            adjusted_prompt = f"{original_prompt}, {adjustment}"
            
            return self.generate(
                image_prompt=adjusted_prompt,
                style_preference=style_preference
            )
            
        except Exception as e:
            logger.error(f"重新生成图像失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


# 创建全局图像生成智能体实例
image_generator = ImageGeneratorAgent()


if __name__ == "__main__":
    # 测试图像生成智能体
    test_prompt = "A beautiful Chinese village mural painting featuring traditional Hui-style architecture with white walls, black tiles, and horse-head walls, artistic, detailed, high quality"
    
    try:
        result = image_generator.generate(test_prompt, style_preference="traditional")
        print("=== 图像生成结果 ===")
        print(f"状态: {result['status']}")
        if result['status'] == 'success':
            print(f"图像数量: {len(result['images'])}")
            for i, img in enumerate(result['images']):
                print(f"图像 {i+1}: {img.get('local_path', img.get('url', ''))}")
    except Exception as e:
        print(f"测试失败: {e}")

