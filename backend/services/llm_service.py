"""
LLM服务
封装通义千问API调用
"""

from typing import Optional, List, Dict
import logging
import yaml
from pathlib import Path
logger = logging.getLogger(__name__)

try:
    import dashscope
except ImportError:
    logger.warning("DashScope未安装，请运行: pip install dashscope")
    dashscope = None
from dashscope import Generation
from http import HTTPStatus

from backend.core.config import settings

# 获取提示词目录
BASE_DIR = Path(__file__).parent.parent
PROMPT_PATH = BASE_DIR / "prompts"


def load_prompts(prompt_file: str = "agent_prompts.yaml") -> Dict:
    """
    从指定的YAML文件中加载提示词配置
    
    参数:
        prompt_file (str): YAML格式的提示词配置文件名称，默认为"agent_prompts.yaml"
        
    返回:
        Dict: 从YAML文件中解析出的字典数据
        
    异常:
        FileNotFoundError: 当指定的文件不存在时抛出
        yaml.YAMLError: 当YAML文件格式错误时抛出
    """
    # 打开并读取YAML配置文件，使用safe_load方法安全解析
    file_path = PROMPT_PATH / prompt_file
    with open(file_path, 'r', encoding='utf-8') as f:
         return yaml.safe_load(f)
    

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
                # Load prompts from YAML (backend/prompts/agent_prompts.yaml)
        try:
            self.prompts = load_prompts()
        except FileNotFoundError:
            logger.error("提示词文件未找到：%s", PROMPT_PATH)
            self.prompts = {}
        except Exception as e:
            logger.error("加载提示词失败：%s", e)
            self.prompts = {}
    
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
        # Load templates from prompts; fall back to original hardcoded templates if missing
        system_template = self.prompts.get('culture_analyst', {}).get('system_prompt') 

        user_template = self.prompts.get('culture_analyst', {}).get('user_prompt') 

        # format user prompt with provided values
        try:
            user_prompt = user_template.format(
                name=village_info.get('name', '未知'),
                location=village_info.get('location', '未知'),
                industry=village_info.get('industry', '未知'),
                history=village_info.get('history', '未知'),
                knowledge_context=knowledge_context
            )
        except Exception:
            # If formatting fails, fall back to concatenating
            user_prompt = f"村庄信息：{village_info}\n参考知识：{knowledge_context}"

        return self.generate_text(
            prompt=user_prompt,
            system_prompt=system_template,
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
        system_template = self.prompts.get('creative_designer', {}).get('system_prompt') 

        user_template = self.prompts.get('creative_designer', {}).get('user_prompt') 

        try:
            user_prompt = user_template.format(
                culture_analysis=culture_analysis,
                user_preference=user_preference if user_preference else '无特殊要求'
            )
        except Exception:
            user_prompt = f"文化分析：{culture_analysis}\n用户偏好：{user_preference}"

        return self.generate_text(
            prompt=user_prompt,
            system_prompt=system_template,
            temperature=0.8,
            max_tokens=2500
        )

    
    def refine_image_prompt(self, design_description: str) -> str:
        """
        优化图像生成Prompt
        
        Args:
            design_description: 设计方案描述
            
        Returns:
            优化后的图像生成Prompt
        """
        system_template = self.prompts.get('image_generator', {}).get('system_prompt')

        user_template = self.prompts.get('image_generator', {}).get('user_prompt')
        try:
            user_prompt = user_template.format(design_description=design_description)
        except Exception:
            user_prompt = f"设计描述：{design_description}"

        return self.generate_text(
            prompt=user_prompt,
            system_prompt=system_template,
            temperature=0.5,
            max_tokens=300
        )
        



# 创建全局LLM服务实例
llm_service = LLMService()


if __name__ == "__main__":
    # 测试LLM服务
    # test_prompt = "请用一句话介绍徽派建筑的特点"
    
    # try:
    #     result = llm_service.generate_text(test_prompt)
    #     print(f"LLM响应: {result}")
    # except Exception as e:
    #     print(f"测试失败: {e}")
    
    print("\n=== 提示词测试 ===")
    # 测试加载提示词
    try:
       llm_service.prompts = load_prompts()
       print("提示词加载成功")
    except Exception as e:
       print(f"提示词加载失败: {e}")
    print(llm_service.prompts.get('creative_designer', {}).get('system_prompt') if isinstance(llm_service.prompts, dict) else None)


    