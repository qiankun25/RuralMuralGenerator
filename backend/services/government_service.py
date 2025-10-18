"""
政府开放数据平台服务
封装政府API调用
"""

import time
import json
import requests
from typing import Dict, Any, Optional
import logging
logger = logging.getLogger(__name__)

try:
    import httpx
except ImportError:
    logger.warning("httpx未安装，请运行: pip install httpx")
    httpx = None
import asyncio
from functools import lru_cache

from backend.core.config import settings


class ZhejiangPlatformClient:
    """
    浙江公共数据统一平台数据接口
    """

    # 平台固定常量
    SIGN_URL = "https://data.zjzwfw.gov.cn/jimp/sign/createsign.do"
    DATA_URL = "https://data.zjzwfw.gov.cn/interface/gateway.do"

    def __init__(
        self,
        *,
        app_id: str,
        interface_id: str,
        version: str,
        app_secret: str,
        user_secret: str,
        charset: str = "utf-8",
        origin: str = "0"
    ):
        self.app_id       = app_id
        self.interface_id = interface_id
        self.version      = version
        self.app_secret   = app_secret
        self.user_secret  = user_secret
        self.charset      = charset
        self.origin       = origin
        self.session      = requests.Session()

    # -------------------- 私有工具 --------------------
    def _timestamp(self) -> str:
        return str(int(time.time() * 1000))

    def _json_str(self, obj: Any) -> str:
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

    def _form(self, **kwargs) -> Dict[str, str]:
        """统一 form 字段组装"""
        return {k: str(v) for k, v in kwargs.items()}

    # -------------------- 统一流程 --------------------
    def _get_sign(self, biz_content: str) -> str:
        """验签接口取 sign"""
        params = {
            "app_id": self.app_id,
            "interface_id": self.interface_id,
            "version": self.version,
            "charset": self.charset,
            "timestamp": self._timestamp(),   
            "origin": self.origin,
            "biz_content": biz_content,       
            "sign": ""                        # 平台要求必须存在
        }
        resp = self.session.post(self.SIGN_URL, data=params)
        sign_text = resp.text.strip()
        if not sign_text:
            raise RuntimeError("验签接口返回空 body")
        # 平台直接返回 64 位 16 进制字符串，无需 JSON 解析
        return sign_text
    def query_count(self, page_num: int = 1, page_size: int = 1) -> int:
        """只返回总条数（data 字段）"""
        biz = self._json_str({
            "userSecret": self.user_secret,
            "appSecret" : self.app_secret,
            "pageNum"   : str(page_num),
            "pageSize"  : str(page_size)
        })
        sign = self._get_sign(biz)

        params = self._form(
            app_id       = self.app_id,
            interface_id = self.interface_id,
            version      = self.version,
            charset      = self.charset,
            timestamp    = self._timestamp(),
            origin       = self.origin,
            sign         = sign,
            biz_content  = biz
        )
        resp = self.session.post(self.DATA_URL, data=params)
        outer = resp.json()                  # 第一层壳
        if outer.get("code") != 200:
            raise RuntimeError(f"HTTP 状态异常: {outer}")

        inner = json.loads(outer["data"])    # 第二层业务 JSON
        if inner.get("code") != "1":         # 注意是字符串 "1"
            raise RuntimeError(f"业务失败: {inner}")

        return int(inner["data"]["count"])  


# -------------------- 预置实例 --------------------
def shaoxing_client(app_secret: str, user_secret: str) -> ZhejiangPlatformClient:
    """绍兴市 → 已固化参数"""
    return ZhejiangPlatformClient(
        app_id       = "sxkfyy",
        interface_id = "biz06043036zjzjsxclyxx",
        version      = "1.0.0",
        app_secret   = app_secret,
        user_secret  = user_secret
    )


class ZhejiangAdapter:
    """
    浙江省数据平台适配器
    封装 ZhejiangPlatformClient，使其兼容 GovernmentDataService 的接口形式
    """

    def __init__(self, app_secret: str, user_secret: str):
        self.client = shaoxing_client(app_secret, user_secret)

    def query_village_data(self, village_name: str) -> Dict:
        try:
            # 查询并过滤结果
            biz = self.client._json_str({
                "userSecret": self.client.user_secret,
                "appSecret": self.client.app_secret,
                "pageNum": "1",
                "pageSize": "200"
            })
            sign = self.client._get_sign(biz)
            params = self.client._form(
                app_id=self.client.app_id,
                interface_id="biz06043036zjzjsxclyxxfy",
                version=self.client.version,
                charset=self.client.charset,
                timestamp=self.client._timestamp(),
                origin=self.client.origin,
                sign=sign,
                biz_content=biz
            )

            resp = self.client.session.post(self.client.DATA_URL, data=params)
            outer = resp.json()
            inner = json.loads(outer["data"])
            datalist = json.loads(inner["data"]["data"])

            # 查找匹配的村落
            match = next((v for v in datalist if v["xcmc"] == village_name), None)
            if match:
                return {"status": "success", "data": match, "source": "zhejiang_platform"}
            else:
                return {"status": "not_found", "data": {}, "source": "zhejiang_platform"}

        except Exception as e:
            logger.error(f"ZhejiangAdapter 查询异常: {e}")
            return {"status": "error", "message": str(e), "source": "zhejiang_platform"}


class GovernmentDataService:
    """政府开放数据平台服务类"""
    
    def __init__(self):
            self.api_key = getattr(settings, "government_api_key", None)
            self.base_url = getattr(settings, "government_api_base_url", None)
            self.timeout = getattr(settings, "government_api_timeout", 10)
            self.retry = getattr(settings, "government_api_retry", 3)

            # 兼容性增强：可配置使用不同省份适配器
            self.province_adapters = {
                "浙江省": ZhejiangAdapter(
                    app_secret="b51f70786870462fa7f6d90bddefce8b",
                    user_secret="d378b256f7af480c826bb306f19c42e9"
                )
            }
    
    async def query_village_data(self, village_name: str, province: Optional[str] = None) -> Dict:
        try:
            # 若为浙江省，走专用适配器
            if province in self.adapters:
                adapter = self.adapters[province]
                return adapter.query_village_data(village_name)

            # 否则走默认HTTP接口
            if not self.api_key:
                return self._get_mock_data(village_name)

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                for attempt in range(self.retry):
                    try:
                        resp = await client.get(
                            f"{self.base_url}/villages/search",
                            params={"name": village_name, "api_key": self.api_key}
                        )
                        resp.raise_for_status()
                        data = resp.json()
                        return {"status": "success", "data": data, "source": "government_api"}
                    except httpx.HTTPError as e:
                        logger.warning(f"政府API请求失败 (尝试 {attempt + 1}/{self.retry}): {e}")
                        if attempt == self.retry - 1:
                            raise
                        await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"查询政府数据异常: {e}")
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

