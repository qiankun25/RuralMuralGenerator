"""
政府开放数据平台服务
封装政府API调用
"""

from typing import Optional, Dict, List
import logging
logger = logging.getLogger(__name__)

try:
    import httpx
except ImportError:
    logger.warning("httpx未安装，请运行: pip install httpx")
    httpx = None
import asyncio
from functools import lru_cache

from core.config import settings


class GovernmentDataService:
    """政府开放数据平台服务类"""
    
    def __init__(self):
        """初始化政府数据服务"""
        self.api_key = settings.government_api_key
        self.base_url = settings.government_api_base_url
        self.timeout = settings.government_api_timeout
        self.retry = settings.government_api_retry
        
        if not self.api_key:
            logger.warning("未配置GOVERNMENT_API_KEY，政府数据查询功能将不可用")
    
    async def query_village_data(
        self,
        village_name: str,
        province: Optional[str] = None
    ) -> Dict:
        """
        查询村落数据
        
        Args:
            village_name: 村落名称
            province: 省份（可选，用于精确匹配）
            
        Returns:
            村落数据字典
        """
        try:
            if not self.api_key:
                logger.warning("未配置API密钥，返回空数据")
                return self._get_mock_data(village_name)
            
            # 构建请求参数
            params = {
                "name": village_name,
                "api_key": self.api_key
            }
            
            if province:
                params["province"] = province
            
            # 发送异步请求
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                for attempt in range(self.retry):
                    try:
                        response = await client.get(
                            f"{self.base_url}/villages/search",
                            params=params
                        )
                        response.raise_for_status()
                        
                        data = response.json()
                        logger.info(f"成功查询村落数据: {village_name}")
                        
                        return {
                            "status": "success",
                            "data": data,
                            "source": "government_api"
                        }
                        
                    except httpx.HTTPError as e:
                        logger.warning(f"政府API请求失败 (尝试 {attempt + 1}/{self.retry}): {e}")
                        if attempt == self.retry - 1:
                            raise
                        await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"查询政府数据异常: {e}")
            # 返回Mock数据作为降级方案
            return self._get_mock_data(village_name)
    
    def query_village_data_sync(
        self,
        village_name: str,
        province: Optional[str] = None
    ) -> Dict:
        """
        同步版本的村落数据查询
        
        Args:
            village_name: 村落名称
            province: 省份（可选）
            
        Returns:
            村落数据字典
        """
        try:
            # 在同步环境中运行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.query_village_data(village_name, province)
            )
            loop.close()
            return result
        except Exception as e:
            logger.error(f"同步查询失败: {e}")
            return self._get_mock_data(village_name)
    
    @lru_cache(maxsize=100)
    def _get_mock_data(self, village_name: str) -> Dict:
        """
        获取Mock数据（用于演示或API不可用时）
        
        Args:
            village_name: 村落名称
            
        Returns:
            Mock数据
        """
        logger.info(f"使用Mock数据: {village_name}")
        
        # 预定义的Mock数据
        mock_database = {
            "西递村": {
                "name": "西递村",
                "province": "安徽省",
                "city": "黄山市",
                "district": "黟县",
                "category": "传统村落",
                "features": ["徽派建筑", "世界文化遗产", "明清古村"],
                "tourism_info": {
                    "annual_visitors": "约50万人次",
                    "main_attractions": ["胡文光刺史牌坊", "履福堂", "桃李园"],
                    "specialty_products": ["徽墨", "歙砚", "茶叶"]
                },
                "cultural_heritage": {
                    "architecture": "徽派建筑群，以马头墙、青砖黛瓦为特色",
                    "history": "始建于北宋，距今已有近千年历史",
                    "culture": "徽商文化、耕读文化"
                }
            },
            "宏村": {
                "name": "宏村",
                "province": "安徽省",
                "city": "黄山市",
                "district": "黟县",
                "category": "传统村落",
                "features": ["徽派建筑", "世界文化遗产", "牛形村落"],
                "tourism_info": {
                    "annual_visitors": "约80万人次",
                    "main_attractions": ["月沼", "南湖", "承志堂"],
                    "specialty_products": ["竹编", "木雕", "茶叶"]
                },
                "cultural_heritage": {
                    "architecture": "独特的牛形村落布局，水系完善",
                    "history": "始建于南宋，距今约900年历史",
                    "culture": "徽商文化、风水文化"
                }
            }
        }
        
        # 如果有匹配的Mock数据，返回
        if village_name in mock_database:
            return {
                "status": "mock",
                "data": mock_database[village_name],
                "source": "mock_database"
            }
        
        # 否则返回通用Mock数据
        return {
            "status": "mock",
            "data": {
                "name": village_name,
                "province": "未知",
                "category": "传统村落",
                "features": ["地方特色", "文化传承"],
                "note": "这是Mock数据，实际数据需要配置政府API密钥"
            },
            "source": "mock_database"
        }
    
    async def query_tourism_info(self, village_name: str) -> Dict:
        """
        查询乡村旅游信息
        
        Args:
            village_name: 村落名称
            
        Returns:
            旅游信息字典
        """
        # 这里可以调用其他政府API接口
        # 目前返回Mock数据
        logger.info(f"查询旅游信息: {village_name}")
        
        return {
            "status": "mock",
            "data": {
                "tourism_status": "开放",
                "best_season": "春秋两季",
                "recommended_duration": "1-2天"
            }
        }


# 创建全局政府数据服务实例
government_service = GovernmentDataService()


if __name__ == "__main__":
    # 测试政府数据服务
    result = government_service.query_village_data_sync("西递村", "安徽省")
    print(f"查询结果: {result}")

