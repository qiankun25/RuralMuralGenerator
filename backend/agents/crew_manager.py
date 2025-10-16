"""
CrewAI工作流管理器
编排多个智能体的协作流程
"""

from typing import Dict, Optional, Callable
from loguru import logger
from crewai import Agent, Task, Crew, Process

from agents.culture_analyst import culture_analyst
from agents.creative_designer import creative_designer
from agents.image_generator import image_generator
from core.config import settings


class MuralGenerationCrew:
    """墙绘生成工作流"""
    
    def __init__(self):
        """初始化CrewAI工作流"""
        self.culture_analyst_agent = None
        self.creative_designer_agent = None
        self.image_generator_agent = None
        self.crew = None
        
        self._setup_agents()
    
    def _setup_agents(self):
        """设置CrewAI Agents"""
        
        # 文化分析Agent
        self.culture_analyst_agent = Agent(
            role='乡村文化分析专家',
            goal='深度分析乡村文化特色，为墙绘设计提供文化基础',
            backstory="""你是一位资深的乡村文化研究学者，拥有丰富的中国传统村落研究经验。
你擅长从历史、建筑、民俗、产业等多个维度分析村落文化，能够提炼出最具代表性的文化元素。
你的分析报告将为墙绘设计提供重要的文化指导。""",
            verbose=True,
            allow_delegation=False
        )
        
        # 创意设计Agent
        self.creative_designer_agent = Agent(
            role='墙绘艺术设计师',
            goal='基于文化分析创作独特的墙绘设计方案',
            backstory="""你是一位经验丰富的墙绘艺术家，擅长将文化元素转化为视觉设计。
你精通色彩搭配、构图布局、文化符号运用，能够创作出既有文化内涵又具有艺术美感的墙绘方案。
你的设计作品曾在多个乡村振兴项目中获得好评。""",
            verbose=True,
            allow_delegation=False
        )
        
        # 图像生成Agent
        self.image_generator_agent = Agent(
            role='AI图像生成专家',
            goal='根据设计方案生成高质量的墙绘图像',
            backstory="""你是一位AI图像生成技术专家，精通各种图像生成模型的使用。
你能够将设计描述转化为精确的图像生成Prompt，并调用AI模型生成高质量的墙绘图像。
你对中国传统艺术风格有深入理解，能够确保生成的图像符合文化特色。""",
            verbose=True,
            allow_delegation=False
        )
    
    def run_full_workflow(
        self,
        village_info: Dict,
        user_preference: Optional[str] = None,
        style_preference: str = "traditional",
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        运行完整的墙绘生成工作流
        
        Args:
            village_info: 村落信息
            user_preference: 用户偏好
            style_preference: 风格偏好
            progress_callback: 进度回调函数
            
        Returns:
            完整的生成结果
        """
        try:
            logger.info("开始运行CrewAI工作流")
            
            result = {
                "status": "processing",
                "culture_analysis": None,
                "design_options": None,
                "selected_design": None,
                "image": None
            }
            
            # 步骤1：文化分析
            if progress_callback:
                progress_callback("文化分析中...", 25)
            
            logger.info("步骤1: 文化分析")
            culture_analysis = culture_analyst.analyze(village_info)
            result["culture_analysis"] = culture_analysis
            
            # 步骤2：创意设计
            if progress_callback:
                progress_callback("生成设计方案中...", 50)
            
            logger.info("步骤2: 创意设计")
            design_options = creative_designer.generate_designs(
                culture_analysis,
                user_preference
            )
            result["design_options"] = design_options
            
            # 步骤3：提取第一个方案的图像Prompt
            # 注：实际使用时，应该由用户选择方案
            if progress_callback:
                progress_callback("准备图像生成...", 75)
            
            logger.info("步骤3: 提取图像Prompt")
            # 简化版：直接使用设计方案的前500字符
            image_prompt = creative_designer.extract_image_prompt(design_options[:500])
            
            # 步骤4：图像生成
            if progress_callback:
                progress_callback("生成图像中...", 90)
            
            logger.info("步骤4: 图像生成")
            image_result = image_generator.generate(
                image_prompt=image_prompt,
                style_preference=style_preference
            )
            result["image"] = image_result
            
            # 完成
            if progress_callback:
                progress_callback("完成", 100)
            
            result["status"] = "completed"
            logger.info("CrewAI工作流完成")
            
            return result
            
        except Exception as e:
            logger.error(f"CrewAI工作流失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def run_step_by_step(
        self,
        step: str,
        input_data: Dict
    ) -> Dict:
        """
        分步执行工作流（用于前端渐进式交互）
        
        Args:
            step: 步骤名称 (analyze/design/generate)
            input_data: 输入数据
            
        Returns:
            该步骤的执行结果
        """
        try:
            if step == "analyze":
                # 文化分析步骤
                village_info = input_data.get("village_info", {})
                result = culture_analyst.analyze(village_info)
                return {
                    "status": "success",
                    "step": "analyze",
                    "result": result
                }
            
            elif step == "design":
                # 创意设计步骤
                culture_analysis = input_data.get("culture_analysis", "")
                user_preference = input_data.get("user_preference", "")
                result = creative_designer.generate_designs(
                    culture_analysis,
                    user_preference
                )
                return {
                    "status": "success",
                    "step": "design",
                    "result": result
                }
            
            elif step == "generate":
                # 图像生成步骤
                design_option = input_data.get("design_option", "")
                style_preference = input_data.get("style_preference", "traditional")
                
                # 提取图像Prompt
                image_prompt = creative_designer.extract_image_prompt(design_option)
                
                # 生成图像
                result = image_generator.generate(
                    image_prompt=image_prompt,
                    style_preference=style_preference
                )
                return {
                    "status": "success",
                    "step": "generate",
                    "result": result
                }
            
            else:
                return {
                    "status": "error",
                    "error": f"未知步骤: {step}"
                }
                
        except Exception as e:
            logger.error(f"步骤执行失败 ({step}): {e}")
            return {
                "status": "error",
                "step": step,
                "error": str(e)
            }


# 创建全局工作流管理器实例
crew_manager = MuralGenerationCrew()


if __name__ == "__main__":
    # 测试CrewAI工作流
    test_village_info = {
        "name": "西递村",
        "location": "安徽省黄山市",
        "industry": "旅游、徽派建筑保护",
        "history": "明清古村落，以马头墙和木雕闻名"
    }
    
    def progress_callback(message, progress):
        print(f"[{progress}%] {message}")
    
    try:
        result = crew_manager.run_full_workflow(
            village_info=test_village_info,
            progress_callback=progress_callback
        )
        
        print("\n=== 工作流执行结果 ===")
        print(f"状态: {result['status']}")
        if result['status'] == 'completed':
            print("\n文化分析:")
            print(result['culture_analysis'][:200] + "...")
            print("\n设计方案:")
            print(result['design_options'][:200] + "...")
            print("\n图像生成:")
            print(result['image'])
    except Exception as e:
        print(f"测试失败: {e}")

