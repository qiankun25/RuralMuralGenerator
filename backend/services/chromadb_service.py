"""
ChromaDB服务
提供向量数据库的初始化、检索等功能
"""

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    from chromadb.utils import embedding_functions
except ImportError:
    chromadb = None
    ChromaSettings = None
    embedding_functions = None

from typing import List, Dict, Optional
import logging
logger = logging.getLogger(__name__)
import os

from backend.core.config import settings


class ChromaDBService:
    """ChromaDB服务类"""
    
    def __init__(self):
        """初始化ChromaDB客户端"""
        self.client = None
        self.villages_collection = None
        self.designs_collection = None
        self.embedding_function = None
        
    def initialize(self):
        """初始化ChromaDB"""
        try:
            # 确保目录存在
            os.makedirs(settings.chromadb_path, exist_ok=True)
            
            # 创建ChromaDB客户端（持久化模式）
            self.client = chromadb.PersistentClient(
                path=settings.chromadb_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 配置Embedding函数
            # 使用sentence-transformers的中文模型
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="paraphrase-multilingual-MiniLM-L12-v2"
            )
            
            # 获取或创建村落知识库集合
            self.villages_collection = self.client.get_or_create_collection(
                name=settings.chromadb_collection_villages,
                embedding_function=self.embedding_function,
                metadata={"description": "村落文化知识库"}
            )
            
            # 获取或创建设计案例集合
            self.designs_collection = self.client.get_or_create_collection(
                name=settings.chromadb_collection_designs,
                embedding_function=self.embedding_function,
                metadata={"description": "墙绘设计案例库"}
            )
            
            logger.info(f"ChromaDB初始化成功")
            logger.info(f"村落知识库文档数: {self.villages_collection.count()}")
            logger.info(f"设计案例库文档数: {self.designs_collection.count()}")
            
        except Exception as e:
            logger.error(f"ChromaDB初始化失败: {e}")
            raise
    
    def add_villages(self, villages_data: List[Dict]):
        """
        添加村落知识到向量库
        
        Args:
            villages_data: 村落数据列表，每个元素包含 id, name, content, metadata
        """
        try:
            if not self.villages_collection:
                raise ValueError("ChromaDB未初始化")
            
            ids = [v["id"] for v in villages_data]
            documents = [v["content"] for v in villages_data]
            metadatas = [v.get("metadata", {}) for v in villages_data]
            
            self.villages_collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"成功添加 {len(villages_data)} 个村落知识")
            
        except Exception as e:
            logger.error(f"添加村落知识失败: {e}")
            raise
    
    def add_design_cases(self, design_data: List[Dict]):
        """
        添加设计案例到向量库
        
        Args:
            design_data: 设计案例数据列表
        """
        try:
            if not self.designs_collection:
                raise ValueError("ChromaDB未初始化")
            
            ids = [d["id"] for d in design_data]
            documents = [d["content"] for d in design_data]
            metadatas = [d.get("metadata", {}) for d in design_data]
            
            self.designs_collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"成功添加 {len(design_data)} 个设计案例")
            
        except Exception as e:
            logger.error(f"添加设计案例失败: {e}")
            raise
    
    def search_villages(
        self, 
        query: str, 
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        搜索村落知识库
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            where: 过滤条件
            
        Returns:
            搜索结果字典
        """
        try:
            if not self.villages_collection:
                raise ValueError("ChromaDB未初始化")
            
            results = self.villages_collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            logger.info(f"村落知识库搜索: '{query}' -> {len(results['ids'][0])} 个结果")
            
            return {
                "ids": results["ids"][0],
                "documents": results["documents"][0],
                "metadatas": results["metadatas"][0],
                "distances": results["distances"][0]
            }
            
        except Exception as e:
            logger.error(f"搜索村落知识库失败: {e}")
            raise
    
    def search_design_cases(
        self, 
        query: str, 
        n_results: int = 3,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        搜索设计案例库
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            where: 过滤条件
            
        Returns:
            搜索结果字典
        """
        try:
            if not self.designs_collection:
                raise ValueError("ChromaDB未初始化")
            
            results = self.designs_collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            logger.info(f"设计案例库搜索: '{query}' -> {len(results['ids'][0])} 个结果")
            
            return {
                "ids": results["ids"][0],
                "documents": results["documents"][0],
                "metadatas": results["metadatas"][0],
                "distances": results["distances"][0]
            }
            
        except Exception as e:
            logger.error(f"搜索设计案例库失败: {e}")
            raise
    
    def get_village_by_id(self, village_id: str) -> Optional[Dict]:
        """根据ID获取村落信息"""
        try:
            result = self.villages_collection.get(ids=[village_id])
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "document": result["documents"][0],
                    "metadata": result["metadatas"][0]
                }
            return None
        except Exception as e:
            logger.error(f"获取村落信息失败: {e}")
            return None
    
    def reset_collections(self):
        """重置所有集合（仅用于开发/测试）"""
        try:
            if self.client:
                self.client.delete_collection(settings.chromadb_collection_villages)
                self.client.delete_collection(settings.chromadb_collection_designs)
                logger.warning("已重置所有ChromaDB集合")
                self.initialize()
        except Exception as e:
            logger.error(f"重置集合失败: {e}")
            raise


# 创建全局ChromaDB服务实例
chromadb_service = ChromaDBService()


if __name__ == "__main__":
    # 测试ChromaDB服务
    chromadb_service.initialize()
    
    # 测试添加数据
    test_villages = [
        {
            "id": "test_001",
            "content": "西递村位于安徽省黄山市，是典型的徽派建筑古村落，以马头墙、青砖黛瓦、精美木雕闻名。",
            "metadata": {"name": "西递村", "province": "安徽", "tags": "徽派建筑"}
        }
    ]
    
    chromadb_service.add_villages(test_villages)
    
    # 测试搜索
    results = chromadb_service.search_villages("徽派建筑特色", n_results=1)
    print(f"搜索结果: {results}")

