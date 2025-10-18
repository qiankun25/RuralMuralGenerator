"""
ChromaDB检索工具
用于LangChain Agent
"""

from langchain.tools import Tool
from typing import Optional
from loguru import logger

from services import chromadb_service


def search_village_knowledge(query: str) -> str:
    """
    搜索村落知识库
    
    Args:
        query: 查询文本
        
    Returns:
        检索结果的文本描述
    """
    try:
        results = chromadb_service.search_villages(query, n_results=3)
        
        if not results["documents"]:
            return "未找到相关村落知识"
        
        # 格式化检索结果
        formatted_results = []
        for i, (doc, metadata, distance) in enumerate(zip(
            results["documents"],
            results["metadatas"],
            results["distances"]
        )):
            formatted_results.append(
                f"【参考资料 {i+1}】\n"
                f"相关度: {1 - distance:.2f}\n"
                f"内容: {doc}\n"
                f"来源: {metadata.get('name', '未知')}\n"
            )
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"搜索村落知识库失败: {e}")
        return f"搜索失败: {str(e)}"


def search_design_cases(query: str) -> str:
    """
    搜索设计案例库
    
    Args:
        query: 查询文本
        
    Returns:
        检索结果的文本描述
    """
    try:
        results = chromadb_service.search_design_cases(query, n_results=2)
        
        if not results["documents"]:
            return "未找到相关设计案例"
        
        # 格式化检索结果
        formatted_results = []
        for i, (doc, metadata, distance) in enumerate(zip(
            results["documents"],
            results["metadatas"],
            results["distances"]
        )):
            formatted_results.append(
                f"【设计案例 {i+1}】\n"
                f"相关度: {1 - distance:.2f}\n"
                f"内容: {doc}\n"
            )
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"搜索设计案例库失败: {e}")
        return f"搜索失败: {str(e)}"


# 创建LangChain Tool
village_knowledge_tool = Tool(
    name="search_village_knowledge",
    func=search_village_knowledge,
    description="""搜索村落文化知识库。
    输入：关于村落文化、建筑、历史、民俗等的查询文本
    输出：相关的村落知识和参考资料
    使用场景：当需要了解某个村落的文化特色、建筑风格、历史背景时使用此工具"""
)

design_cases_tool = Tool(
    name="search_design_cases",
    func=search_design_cases,
    description="""搜索墙绘设计案例库。
    输入：关于设计风格、色彩搭配、构图等的查询文本
    输出：相关的设计案例和参考
    使用场景：当需要参考优秀的墙绘设计案例时使用此工具"""
)


if __name__ == "__main__":
    # 测试工具
    result = search_village_knowledge("徽派建筑特色")
    print(result)

