'''
经理智能体
意图解析+路由决策
'''

from loguru import logger
from models.state import MuralGenerationState,Action

from services import llm_service
from typing import Dict, Any

class ManagerAgent:
    """经理智能体-意图解析与路由决策"""

    def __init__(self):
        """初始化经理智能体"""
        pass

    def analyze_intent(self, user_input: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析用户意图并做出路由决策
        
        Args:
            user_input: 用户输入文本
            current_state: 当前对话状态
            
        Returns:
            路由决策结果，包含目标智能体和相关参数
        """
        intent = llm_service.manager_analyze_intent(user_input, current_state)
        logger.info(f"意图分析结果: {intent}")
        return intent
    

# 创建全局经理智能体实例
manager_agent = ManagerAgent()

if __name__ == "__main__":
    # 测试经理智能体
    test_state = {
        "stage": "CULTURE_WAIT",
        "last_agent": "文化分析师"
    }
    
    test_input = "分析准确，请继续设计"
    
    try:
        result = manager_agent.analyze_intent(test_input, test_state)
        print("=== 意图解析结果 ===")
        print(result)
    except Exception as e:
        print(f"测试失败: {e}")
        
       