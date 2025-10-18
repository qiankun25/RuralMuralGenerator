# zhejiang_platform_client.py
import time
import json
import requests
from typing import Dict, Any, Optional


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

        return int(inner["data"]["count"])   # 拿到 52


# -------------------- 预置两条实例 --------------------
def shaoxing_client(app_secret: str, user_secret: str) -> ZhejiangPlatformClient:
    """绍兴市 → 已固化参数"""
    return ZhejiangPlatformClient(
        app_id       = "sxkfyy",
        interface_id = "biz06043036zjzjsxclyxx",
        version      = "1.0.0",
        app_secret   = app_secret,
        user_secret  = user_secret
    )
def lishui_client(app_secret: str, user_secret: str) -> ZhejiangPlatformClient:
    """丽水市 → 已固化参数"""
    return ZhejiangPlatformClient(
        app_id       = "lishui",
        interface_id = "lscategettotal",
        version      = "1.0.0",
        app_secret   = app_secret,
        user_secret  = user_secret
    )
def search_village(client: ZhejiangPlatformClient, village_name: str):
    """查询指定 villages_name 的 villages_info"""
    biz = cli._json_str({
        "userSecret": cli.user_secret,
        "appSecret" : cli.app_secret,
        "pageNum"   : "1",
        "pageSize"  : "200",
       
    })
    sign = cli._get_sign(biz)
    params = cli._form(
        app_id       = cli.app_id,
        interface_id = "biz06043036zjzjsxclyxxfy",  
        version      = cli.version,
        charset      = cli.charset,
        timestamp    = cli._timestamp(),
        origin       = cli.origin,
        sign         = sign,
        biz_content  = biz
    )

    resp  = cli.session.post(cli.DATA_URL, data=params)
    outer = resp.json()
    inner = json.loads(outer["data"])#msg,code data
    for key, value in inner['data'].items():
        print(f"key: {key}, value: {value}")
    print(type(outer["data"]))
    print(type(inner))
    print(type(inner["data"]))#inner[data]就是一个dict,
    datalist = json.loads(inner['data']['data'])#数组，在此数组中遍历每一个dict中,查找'xcmc'等于village_name
    for i in range(len(datalist)):
        if datalist[i]['xcmc'] == village_name:
            print(datalist[i])
    print(type(datalist))
    print(type(datalist[0]))
    print(datalist[0])

   


# 测试脚本
if __name__ == "__main__":
    cli = shaoxing_client(
        app_secret  ="b51f70786870462fa7f6d90bddefce8b",
        user_secret ="d378b256f7af480c826bb306f19c42e9"
    )
    cli_lishui = lishui_client(
        app_secret  ="b51f70786870462fa7f6d90bddefce8b",
        user_secret ="d378b256f7af480c826bb306f19c42e9"
    )
    total = cli_lishui.query_count()
    print(f">>> 平台共返回 {total} 条记录，开始全量拉取...")
    search_village(cli, "枫桥镇洄村")
 

