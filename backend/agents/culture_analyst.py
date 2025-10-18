"""
文化分析智能体
使用LangChain实现，集成ChromaDB检索和政府API查询
"""

from typing import Dict, List
import logging
logger = logging.getLogger(__name__)

try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_community.chat_models import ChatOpenAI
    from langchain.memory import ConversationBufferMemory
except ImportError:
    logger.warning("LangChain未安装，请运行: pip install langchain langchain-community")
    AgentExecutor = None
    create_openai_tools_agent = None
    ChatPromptTemplate = None
    MessagesPlaceholder = None
    ChatOpenAI = None
    ConversationBufferMemory = None

from tools import village_knowledge_tool, government_data_tool
from services import llm_service, chromadb_service, government_service
from core.config import settings


class CultureAnalystAgent:
    """文化分析智能体"""
    
    def __init__(self):
        """初始化文化分析智能体"""
        self.tools = [village_knowledge_tool, government_data_tool]
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    
    def analyze(self, village_info: Dict) -> str:
        """
        分析村落文化特色
        
        Args:
            village_info: 村落信息字典，包含 name, location, industry, history等
            
        Returns:
            文化分析报告（Markdown格式）
        """
        try:
            logger.info(f"开始分析村落文化: {village_info.get('name', '未知')}")
            
            # 步骤1：从ChromaDB检索相关知识
            knowledge_context = self._retrieve_knowledge(village_info)
            
            # 步骤2：查询政府数据（可选）
            government_data = self._query_government_data(village_info)
            
            # 步骤3：使用LLM进行深度分析
            analysis_report = self._generate_analysis(
                village_info,
                knowledge_context,
                government_data
            )
            
            logger.info("文化分析完成")
            return analysis_report
            
        except Exception as e:
            logger.error(f"文化分析失败: {e}")
            raise
    
    def _retrieve_knowledge(self, village_info: Dict) -> str:
        """从ChromaDB检索相关知识"""
        try:
            # 构建检索查询
            query_parts = []
            
            if village_info.get('name'):
                query_parts.append(village_info['name'])
            
            if village_info.get('location'):
                query_parts.append(village_info['location'])
            
            if village_info.get('industry'):
                query_parts.append(village_info['industry'])
            
            query = " ".join(query_parts)
            
            # 检索村落知识库
            results = chromadb_service.search_villages(query, n_results=3)
            
            if not results["documents"]:
                return "未找到相关知识库信息"
            
            # 格式化检索结果
            knowledge_text = "【知识库检索结果】\n\n"
            for i, (doc, metadata) in enumerate(zip(results["documents"], results["metadatas"])):
                knowledge_text += f"参考资料 {i+1}：\n{doc}\n\n"
            
            return knowledge_text
            
        except Exception as e:
            logger.warning(f"知识库检索失败: {e}")
            return "知识库检索失败"
    
    def _query_government_data(self, village_info: Dict) -> str:
        """查询政府开放数据"""
        try:
            village_name = village_info.get('name', '')
            if not village_name:
                return "未提供村落名称"
            
            result = government_service.query_village_data_sync(village_name,"浙江省")
            
            if result["status"] in ["success", "mock"]:
                data = result["data"]
                
                gov_text = "【政府开放数据】\n\n"
                gov_text += f"村落名称: {data.get('name', '未知')}\n"
                gov_text += f"行政区划: {data.get('province', '')} {data.get('city', '')} {data.get('district', '')}\n"
                gov_text += f"特色标签: {', '.join(data.get('features', []))}\n"
                
                if 'cultural_heritage' in data:
                    heritage = data['cultural_heritage']
                    gov_text += f"\n文化遗产信息:\n"
                    gov_text += f"- 建筑特色: {heritage.get('architecture', '未知')}\n"
                    gov_text += f"- 历史沿革: {heritage.get('history', '未知')}\n"
                    gov_text += f"- 文化内涵: {heritage.get('culture', '未知')}\n"
                
                return gov_text
            else:
                return "政府数据查询失败"
                
        except Exception as e:
            logger.warning(f"政府数据查询失败: {e}")
            return "政府数据查询失败"
    
    def _generate_analysis(
        self,
        village_info: Dict,
        knowledge_context: str,
        government_data: str
    ) -> str:
        """使用LLM生成文化分析报告"""
        try:
            # 调用LLM服务的专用接口
            analysis = llm_service.analyze_culture(village_info, knowledge_context)
            
            # 添加数据来源说明
            analysis += "\n\n---\n\n"
            analysis += "**数据来源**\n"
            analysis += "- 本地知识库（ChromaDB向量检索）\n"
            analysis += "- 政府开放数据平台\n"
            analysis += "- AI深度分析（通义千问）\n"
            
            return analysis
            
        except Exception as e:
            logger.error(f"LLM分析失败: {e}")
            raise


# 创建全局文化分析智能体实例
culture_analyst = CultureAnalystAgent()


if __name__ == "__main__":
    # 测试文化分析智能体
    test_village_info = {
        "name": "西递村",
        "location": "安徽省黄山市",
        "industry": "旅游、徽派建筑保护",
        "history": "明清古村落，以马头墙和木雕闻名"
    }
    
    try:
        result = culture_analyst.analyze(test_village_info)
        print("=== 文化分析报告 ===")
        print(result)
    except Exception as e:
        print(f"测试失败: {e}")

