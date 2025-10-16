"""
LLM服务
封装通义千问API调用
"""

from typing import Optional, List, Dict
import logging
logger = logging.getLogger(__name__)

try:
    import dashscope
except ImportError:
    logger.warning("DashScope未安装，请运行: pip install dashscope")
    dashscope = None
from dashscope import Generation
from http import HTTPStatus

from backend.core.config import settings


class LLMService:
    """LLM服务类"""
    
    def __init__(self):
        """初始化LLM服务"""
        self.api_key = settings.dashscope_api_key
        self.model_name = settings.llm_model_name
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        
        # 设置API Key
        if self.api_key:
            dashscope.api_key = self.api_key
        else:
            logger.warning("未配置DASHSCOPE_API_KEY，LLM功能将不可用")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        调用通义千问进行对话
        
        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "..."}]
            temperature: 温度参数（可选）
            max_tokens: 最大token数（可选）
            stream: 是否流式输出
            
        Returns:
            LLM生成的文本
        """
        try:
            if not self.api_key:
                raise ValueError("未配置DASHSCOPE_API_KEY")
            
            response = Generation.call(
                model=self.model_name,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                result_format='message',
                stream=stream
            )
            
            if response.status_code == HTTPStatus.OK:
                result = response.output.choices[0].message.content
                logger.info(f"LLM调用成功，生成文本长度: {len(result)}")
                return result
            else:
                error_msg = f"LLM调用失败: {response.code} - {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"LLM调用异常: {e}")
            raise
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        简化的文本生成接口
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词（可选）
            temperature: 温度参数（可选）
            max_tokens: 最大token数（可选）
            
        Returns:
            生成的文本
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        return self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def analyze_culture(self, village_info: Dict, knowledge_context: str) -> str:
        """
        文化分析专用接口
        
        Args:
            village_info: 村落信息
            knowledge_context: 从ChromaDB检索的知识上下文
            
        Returns:
            文化分析报告
        """
        system_prompt = """你是一位资深的乡村文化研究专家，擅长分析中国传统村落的文化特色。
你的任务是深度分析村落的文化内涵，为墙绘设计提供专业的文化指导。"""
        
        user_prompt = f"""请分析以下乡村的文化特色：

【村落基本信息】
- 名称：{village_info.get('name', '未知')}
- 地理位置：{village_info.get('location', '未知')}
- 特色产业：{village_info.get('industry', '未知')}
- 历史故事：{village_info.get('history', '未知')}

【参考知识库】
{knowledge_context}

请从以下维度进行分析，并以结构化的Markdown格式输出：

## 核心文化元素
（列出3-5个最具代表性的文化元素）

## 推荐色彩方案
（推荐3-5种主色调，说明色彩的文化寓意）

## 推荐文化符号
（列出5-8个可用于墙绘的文化符号或图案）

## 设计建议
（提供墙绘设计的整体建议，包括风格、构图、氛围等）

## 文化故事线索
（提炼1-2个可以通过墙绘讲述的文化故事）
"""
        
        return self.generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2000
        )
    
    def generate_design_options(self, culture_analysis: str, user_preference: str = "") -> str:
        """
        生成设计方案专用接口
        
        Args:
            culture_analysis: 文化分析报告
            user_preference: 用户偏好（可选）
            
        Returns:
            设计方案（包含3个备选方案）
        """
        system_prompt = """你是一位经验丰富的墙绘艺术设计师，擅长将文化元素转化为视觉设计方案。
你的任务是基于文化分析，创作出既有文化内涵又具有艺术美感的墙绘设计方案。"""
        
        user_prompt = f"""基于以下文化分析报告，请生成3个不同风格的墙绘设计方案：

【文化分析报告】
{culture_analysis}

【用户偏好】
{user_preference if user_preference else '无特殊要求'}

请为每个方案提供以下内容，以Markdown格式输出：

## 方案A：传统文化风格
- **设计主题**：（一句话概括）
- **核心元素**：（列出3-5个主要视觉元素）
- **色彩搭配**：（主色调+辅助色）
- **构图建议**：（描述画面布局）
- **文化寓意**：（说明设计的文化内涵）
- **图像生成Prompt**：（英文，用于AI图像生成，50-100词）

## 方案B：现代简约风格
（同上结构）

## 方案C：文化叙事风格
（同上结构）
"""
        
        return self.generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=2500
        )
    
    def refine_image_prompt(self, design_description: str) -> str:
        """
        优化图像生成Prompt
        
        Args:
            design_description: 设计方案描述
            
        Returns:
            优化后的英文Prompt
        """
        system_prompt = """你是一位AI图像生成专家，擅长将设计描述转化为高质量的图像生成Prompt。"""
        
        user_prompt = f"""请将以下墙绘设计描述转化为详细的英文图像生成Prompt：

{design_description}

要求：
1. 使用英文
2. 包含风格、主体、色彩、构图等关键信息
3. 长度控制在50-100个英文单词
4. 适合用于Stable Diffusion或通义万相等AI图像生成模型
5. 添加质量提升关键词（如 high quality, detailed, artistic 等）

请直接输出英文Prompt，不要有其他解释：
"""
        
        return self.generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=300
        )


# 创建全局LLM服务实例
llm_service = LLMService()


if __name__ == "__main__":
    # 测试LLM服务
    test_prompt = "请用一句话介绍徽派建筑的特点"
    
    try:
        result = llm_service.generate_text(test_prompt)
        print(f"LLM响应: {result}")
    except Exception as e:
        print(f"测试失败: {e}")

