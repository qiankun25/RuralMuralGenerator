"""
政府API查询工具
用于LangChain Agent
"""

from langchain.tools import Tool
from typing import Optional
from loguru import logger
import json

from services import government_service


def query_government_data(village_name: str) -> str:
    """
    查询政府开放数据平台
    
    Args:
        village_name: 村落名称
        
    Returns:
        政府数据的文本描述
    """
    try:
        result = government_service.query_village_data_sync(village_name, "浙江省")
        
        if result["status"] in ["success", "mock"]:
            data = result["data"]
            
            # 格式化政府数据
            formatted_data = f"""【政府开放数据平台查询结果】
村落名称: {data.get('name', '未知')}
行政区划: {data.get('province', '')} {data.get('city', '')} {data.get('district', '')}
村落类别: {data.get('category', '未知')}
特色标签: {', '.join(data.get('features', []))}

"""
            
            # 添加旅游信息
            if 'tourism_info' in data:
                tourism = data['tourism_info']
                formatted_data += f"""【旅游信息】
年游客量: {tourism.get('annual_visitors', '未知')}
主要景点: {', '.join(tourism.get('main_attractions', []))}
特色产品: {', '.join(tourism.get('specialty_products', []))}

"""
            
            # 添加文化遗产信息
            if 'cultural_heritage' in data:
                heritage = data['cultural_heritage']
                formatted_data += f"""【文化遗产】
建筑特色: {heritage.get('architecture', '未知')}
历史沿革: {heritage.get('history', '未知')}
文化内涵: {heritage.get('culture', '未知')}
"""
            
            # 添加数据来源说明
            if result["source"] == "mock_database":
                formatted_data += "\n注意：这是Mock数据，实际使用需配置政府API密钥"
            
            return formatted_data
        else:
            return "查询失败，未获取到数据"
            
    except Exception as e:
        logger.error(f"查询政府数据失败: {e}")
        return f"查询失败: {str(e)}"


# 创建LangChain Tool
government_data_tool = Tool(
    name="query_government_data",
    func=query_government_data,
    description="""查询政府开放数据平台获取村落官方数据。
    输入：村落名称
    输出：村落的官方数据，包括行政区划、旅游信息、文化遗产等
    使用场景：当需要获取村落的权威数据和官方信息时使用此工具"""
)


if __name__ == "__main__":
    # 测试工具
    result = query_government_data("西递村")
    print(result)

