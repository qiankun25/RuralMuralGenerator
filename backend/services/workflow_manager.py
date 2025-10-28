"""
CrewAI工作流管理器
基于状态机 + Manager 智能体的动态流程控制
"""

from typing import Dict, Any, Optional
from loguru import logger

import json

from models.state import MuralGenerationState, Stage, AgentName, Action
from agents.culture_analyst import culture_analyst
from agents.creative_designer import creative_designer
from agents.image_generator import image_generator
from agents.manager_agent import ManagerAgent
from api.models import VillageInfo



def _handle_initial_input(user_input: str, state: MuralGenerationState) -> bool:
    """处理 INITIAL 阶段的用户输入：必须是结构化村落信息（JSON）"""
    try:
        data = json.loads(user_input)
        village_info = VillageInfo(**data).model_dump()
        state.workflow_data["village_info"] = village_info

        # 自动执行文化分析
        result = culture_analyst.analyze(village_info)
        state.workflow_data["culture_analysis"] = result

        agent_output = f"✅ 村落信息已接收！\n\n文化分析完成：\n\n{result}\n\n请确认是否继续生成设计方案？"
        state.add_agent_output(AgentName.CULTURE_ANALYST, agent_output)
        state.stage = Stage.CULTURE

        return False

    except (json.JSONDecodeError, ValueError) as e:
        agent_output = (
            "❌ 村落信息格式错误。\n\n"
            "请通过前端表单提交结构化数据（包含名称、位置、历史、产业、文化特色）。\n"
            "系统无法从自由文本中可靠提取必要信息。"
        )
        state.add_agent_output(AgentName.MANAGER, agent_output)
        return False


def run_workflow(user_input: str, state: MuralGenerationState) -> bool:
    """
    主循环入口：每次处理一轮用户输入，更新状态，返回是否完成
    """
    logger.info(f"收到用户输入: {user_input}")
    state.add_user_input(user_input)


    if state.stage == Stage.INITIAL:
        return _handle_initial_input(user_input, state)

    # Step 1: Manager 决策（仅在非 INITIAL 阶段使用）
    manager = ManagerAgent()
    decision = manager.analyze_intent(user_input, state.to_dict_for_prompt())
    action = Action(decision["action"])
    next_stage = Stage(decision["next_stage"])

    logger.info(f"Manager 决策: action={action}, next_stage={next_stage}")

    # Step 2: 根据 action 分发处理
    if action == Action.NEW:
        return _handle_new(state)
    elif action == Action.CONFIRM:
        return _handle_confirm(state, next_stage)
    elif action == Action.MODIFY:
        return _handle_modify(state, user_input)
    else:
        logger.error(f"未知 action: {action}")
        return False


def _handle_new(state: MuralGenerationState) -> bool:
    """处理 NEW 动作：重置工作流"""
    state.stage = Stage.INITIAL
    state.messages = [state.messages[-1]] if state.messages else []
    state.last_agent = None
    state.workflow_data = {
        "village_info": None,
        "culture_analysis": None,
        "design_schema": None,
        "image_result": None
    }

    agent_output = "好的，我们重新开始。请通过表单提供村落的基本信息（名称、位置、历史、产业、文化特色）以便进行文化分析。"
    state.add_agent_output(AgentName.MANAGER, agent_output)
    
    logger.info("工作流已重置为 INITIAL")
    return False


def _handle_confirm(state: MuralGenerationState, next_stage: Stage) -> bool:
    """处理 CONFIRM 动作：推进到下一阶段"""
    agent_output = ""
    agent_name = None

    if next_stage == Stage.CULTURE:
        village_info = state.workflow_data.get("village_info")
        if not village_info:
            agent_output = "错误：缺少村落信息。请先提交结构化数据。"
            agent_name = AgentName.MANAGER
        else:
            result = culture_analyst.analyze(village_info)
            state.workflow_data["culture_analysis"] = result
            agent_output = f"文化分析完成：\n\n{result}\n\n请确认是否继续生成设计方案？"
            agent_name = AgentName.CULTURE_ANALYST

    elif next_stage == Stage.DESIGN:
        # 创意设计阶段
        culture_analysis = state.workflow_data.get("culture_analysis")
        if not culture_analysis:
            agent_output = "错误：缺少文化分析结果，无法生成设计方案。请先完成文化分析。"
            agent_name = AgentName.MANAGER
        else:
            result = creative_designer.generate_designs(culture_analysis, state.get_last_user_input())
            state.workflow_data["design_schema"] = result
            
            agent_output = f"设计方案生成完成：\n\n{result}\n\n请选择一个方案继续生成图像，或要求修改设计。"
            agent_name = AgentName.CREATIVE_DESIGNER

    elif next_stage == Stage.IMAGE:
        # 图像生成阶段
        design = state.workflow_data.get("design_schema")
        if not design:
            agent_output = "错误：缺少设计方案，无法生成图像。请先完成设计。"
            agent_name = AgentName.MANAGER
        else:
            image_prompt = creative_designer.extract_image_prompt(design, state.get_last_user_input())
            result = image_generator.generate(image_prompt=image_prompt)#j结果字典
            state.workflow_data["image_result"] = result
            
            agent_output = {
            "type": "image",
            "url": result["images"][0]["url"],  # 提取第一个图片 URL
            "prompt": result["prompt"],
            "text": "图像生成完成！\n\n请确认是否满意，或要求重新生成。"
        }
            agent_name = AgentName.IMAGE_GENERATOR

    else:
        # INITIAL 阶段
        agent_output = "请提供村落的基本信息（如名称、位置、历史、产业等），以便我们开始文化分析。"
        agent_name = AgentName.MANAGER

    # 更新状态
    state.stage = next_stage
    state.add_agent_output(agent_name, agent_output)

    # 判断是否完成
    if state.stage == Stage.IMAGE:
        logger.info("用户确认图像，工作流完成！")
        return True

    return False


def _handle_modify(state: MuralGenerationState, user_input: str) -> bool:
    """处理 MODIFY 动作：在当前阶段重新执行，带上修改意见"""
    current_stage = state.stage
    agent_output = ""
    agent_name = None
    
    # 提取修改意见
    modification_request = user_input

    if current_stage == Stage.CULTURE:
        # 重新进行文化分析，考虑修改意见
        village_info = state.workflow_data.get("village_info") or {}
        if not isinstance(village_info, dict):
            # 如果意外是字符串，尝试迁移到 description 字段
            village_info = {"description": str(village_info)}

        village_info["modification_request"] = modification_request
        result = culture_analyst.analyze(village_info)
        state.workflow_data["culture_analysis"] = result
        
        agent_output = f"已根据您的要求重新分析：\n\n{result}\n\n请确认是否满意？"
        agent_name = AgentName.CULTURE_ANALYST

    elif current_stage == Stage.DESIGN:
        # 重新生成设计，考虑修改意见
        culture_analysis = state.workflow_data.get("culture_analysis", "")
        user_preference = f"用户修改要求：{modification_request}"
        
        result = creative_designer.generate_designs(culture_analysis, user_preference)
        state.workflow_data["design_schema"] = result
        
        agent_output = f"已根据您的要求重新设计：\n\n{result}\n\n请确认是否满意？"
        agent_name = AgentName.CREATIVE_DESIGNER

    elif current_stage == Stage.IMAGE:
        # 重新生成图像，考虑修改意见
        design = state.workflow_data.get("design_schema", "")
        modified_prompt = f"修改要求：{modification_request}"
        image_prompt = creative_designer.extract_image_prompt(design, modified_prompt)
        
        result = image_generator.generate(
            image_prompt=image_prompt
        )
        state.workflow_data["image_result"] = result
        
        agent_output = f"已根据您的要求重新生成：\n\n{result}\n\n请确认是否满意？"
        agent_name = AgentName.IMAGE_GENERATOR

    else:
        # INITIAL 阶段没有可修改内容
        agent_output = "当前处于初始阶段，还没有可修改的内容。请先提供村落信息。"
        agent_name = AgentName.MANAGER

    # 保持当前阶段不变，添加输出
    state.add_agent_output(agent_name, agent_output)
    return False