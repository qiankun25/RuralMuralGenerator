"""
存储程序执行过程状态
"""

from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field

class Stage(Enum):
    INITIAL = 'INITIAL'
    CULTURE = 'CULTURE'
    DESIGN = 'DESIGN'
    IMAGE = 'IMAGE'

# 用户行为类别
class Action(Enum):
    NEW = 'NEW'        # 新任务
    CONFIRM = 'CONFIRM'  # 确认当前结果
    MODIFY = 'MODIFY'    # 修改当前结果

class AgentName(Enum):
    MANAGER = '经理智能体'
    CULTURE_ANALYST = '文化分析师'
    CREATIVE_DESIGNER = '创意设计师'
    IMAGE_GENERATOR = '图像生成器'

@dataclass
class Message:
    role:str # 角色：user/agent
    content:str # 消息内容
    agent_name:Optional[str] = None # 发送消息的智能体名称

@dataclass
class MuralGenerationState:
    """墙绘生成工作流状态"""
    stage: Stage = Stage.INITIAL
    last_agent: Optional[AgentName] = None
    messages: list[Message] = field(default_factory=list)
    workflow_data: Dict[str, Any] = field(default_factory=lambda: {
        "village_info": None,
        "culture_analysis": None,
        "design_schema": None,
        "image_result": None
    })

    def __init__(self):
        self.stage = Stage.INITIAL
        self.last_agent = None
        self.messages = []
        self.workflow_data = {
            "village_info": None,
            "culture_analysis": None,
            "design_schema": None,
            "image_result": None
        }


    def add_user_input(self,user_input: str):
        """添加用户输入消息"""
        self.messages.append(Message(role='user', content=user_input))

    def add_agent_output(self,agent_name: AgentName, output: str):
        """添加智能体输出消息"""
        self.messages.append(Message(role='agent', content=output, agent_name=agent_name.value))
        self.last_agent = agent_name

    def get_last_user_input(self) -> Optional[str]:
        """获取最后一次用户输入"""
        for message in reversed(self.messages):
            if message.role == 'user':
                return message.content
        return None
    
    def get_last_agent_output(self) -> Optional[str]:
        """获取最后一次智能体输出"""
        for message in reversed(self.messages):
            if message.role == 'agent':
                return message.content
        return None
    
    def get_agent_output(self, agent_name: AgentName) -> Optional[str]:
        """获取指定 agent 的最新输出"""
        for msg in reversed(self.messages):
            if msg.role == "agent" and msg.agent_name == agent_name.value:
                return msg.content
        return None

    def to_dict_for_prompt(self) -> Dict[str, Any]:
        """将状态转换为用于提示词的字典格式"""
        return {
            "stage": self.stage.value,
            "last_agent": self.last_agent.value if self.last_agent else None,
            "last_agent_output": self.get_last_agent_output() or "",
            "user_input": self.get_last_user_input() or ""
        }
    
    def to_dict_for_debug(self) -> Dict[str, Any]:
        """将状态转换为用于调试的字典格式"""
        return {
            "stage": self.stage.value,
            "last_agent": self.last_agent.value if self.last_agent else None,
            "user_input": self.get_last_user_input() or "",
            "agent_outputs": self.get_last_agent_output() or "",
        }




