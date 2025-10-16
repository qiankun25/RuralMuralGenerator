"""
创意设计智能体
使用LangChain实现，基于文化分析生成墙绘设计方案
"""

from typing import Dict, List, Optional
from loguru import logger
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from services import llm_service, chromadb_service
from tools import design_cases_tool, sensitive_check_tool
from core.config import settings


class CreativeDesignerAgent:
    """创意设计智能体"""
    
    def __init__(self):
        """初始化创意设计智能体"""
        self.memory = ConversationBufferMemory()
    
    def generate_designs(
        self,
        culture_analysis: str,
        user_preference: Optional[str] = None
    ) -> str:
        """
        生成墙绘设计方案
        
        Args:
            culture_analysis: 文化分析报告
            user_preference: 用户偏好（可选）
            
        Returns:
            设计方案（包含3个备选方案，Markdown格式）
        """
        try:
            logger.info("开始生成设计方案")
            
            # 步骤1：检索设计案例参考
            design_references = self._retrieve_design_cases(culture_analysis)
            
            # 步骤2：使用LLM生成设计方案
            design_options = self._generate_design_options(
                culture_analysis,
                design_references,
                user_preference
            )
            
            # 步骤3：敏感词检测
            self._check_content_safety(design_options)
            
            logger.info("设计方案生成完成")
            return design_options
            
        except Exception as e:
            logger.error(f"设计方案生成失败: {e}")
            raise
    
    def _retrieve_design_cases(self, culture_analysis: str) -> str:
        """检索相关设计案例"""
        try:
            # 从文化分析中提取关键词作为检索查询
            # 简化版：直接使用文化分析的前200字符
            query = culture_analysis[:200]
            
            results = chromadb_service.search_design_cases(query, n_results=2)
            
            if not results["documents"]:
                return "未找到相关设计案例"
            
            # 格式化检索结果
            cases_text = "【设计案例参考】\n\n"
            for i, doc in enumerate(results["documents"]):
                cases_text += f"案例 {i+1}：\n{doc}\n\n"
            
            return cases_text
            
        except Exception as e:
            logger.warning(f"设计案例检索失败: {e}")
            return "设计案例检索失败"
    
    def _generate_design_options(
        self,
        culture_analysis: str,
        design_references: str,
        user_preference: Optional[str]
    ) -> str:
        """使用LLM生成设计方案"""
        try:
            # 调用LLM服务的专用接口
            design_options = llm_service.generate_design_options(
                culture_analysis,
                user_preference or "无特殊要求"
            )
            
            return design_options
            
        except Exception as e:
            logger.error(f"LLM生成设计方案失败: {e}")
            raise
    
    def _check_content_safety(self, content: str):
        """检查内容安全性"""
        try:
            from backend.tools.sensitive_check_tool import checker
            
            result = checker.check_text(content)
            
            if not result["is_safe"]:
                logger.warning(f"设计方案包含敏感词: {result['found_words']}")
                # 这里可以选择抛出异常或记录警告
                # 目前仅记录警告
            else:
                logger.info("设计方案内容审核通过")
                
        except Exception as e:
            logger.warning(f"内容审核失败: {e}")
    
    def extract_image_prompt(self, design_option: str) -> str:
        """
        从设计方案中提取图像生成Prompt
        
        Args:
            design_option: 单个设计方案的文本
            
        Returns:
            优化后的英文图像生成Prompt
        """
        try:
            logger.info("提取并优化图像生成Prompt")
            
            # 使用LLM优化Prompt
            image_prompt = llm_service.refine_image_prompt(design_option)
            
            logger.info(f"图像生成Prompt: {image_prompt}")
            return image_prompt
            
        except Exception as e:
            logger.error(f"提取图像Prompt失败: {e}")
            # 返回默认Prompt
            return "A beautiful Chinese village mural painting with traditional cultural elements"
    
    def refine_design(
        self,
        original_design: str,
        user_feedback: str
    ) -> str:
        """
        根据用户反馈优化设计方案
        
        Args:
            original_design: 原始设计方案
            user_feedback: 用户反馈
            
        Returns:
            优化后的设计方案
        """
        try:
            logger.info(f"根据用户反馈优化设计: {user_feedback}")
            
            system_prompt = "你是一位墙绘设计师，需要根据用户的反馈优化设计方案。"
            
            user_prompt = f"""原始设计方案：
{original_design}

用户反馈：
{user_feedback}

请根据用户反馈，优化设计方案，保持原有的结构格式。
"""
            
            refined_design = llm_service.generate_text(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            return refined_design
            
        except Exception as e:
            logger.error(f"设计优化失败: {e}")
            raise


# 创建全局创意设计智能体实例
creative_designer = CreativeDesignerAgent()


if __name__ == "__main__":
    # 测试创意设计智能体
    test_culture_analysis = """
## 核心文化元素
- 徽派建筑：马头墙、青砖黛瓦
- 徽商文化：诚信经营、耕读传家
- 传统工艺：木雕、石雕、砖雕

## 推荐色彩方案
- 青灰色 #2C3E50（主色调）
- 白墙色 #ECF0F1（辅助色）
- 朱红色 #E74C3C（点缀色）
"""
    
    try:
        result = creative_designer.generate_designs(test_culture_analysis)
        print("=== 设计方案 ===")
        print(result)
    except Exception as e:
        print(f"测试失败: {e}")

