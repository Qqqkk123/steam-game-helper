import httpx
from fastapi import HTTPException
import logging
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SteamAPIService:
    # 简单的内存缓存，Key: app_id, Value: {"expire_at": 时间戳, "data": 数据dict}
    # 缓存有效时间设定为 5 分钟 (300秒)，防止频繁刷接口
    _CACHE = {}
    _CACHE_TTL = 300

    @classmethod
    async def fetch_game_price_by_id(cls, app_id: str) -> dict:
        """
        利用 httpx 异步非阻塞请求 Steam 接口，自带高并发基因与内存缓存
        """
        current_time = time.time()

        # 1. 缓存命中策略 (Cache-First)
        if app_id in cls._CACHE:
            cache_item = cls._CACHE[app_id]
            if current_time < cache_item["expire_at"]:
                logger.info(f"🚀 [Cache Hit] 成功命中内存缓存: AppID={app_id}")
                return cache_item["data"]

        # 2. 异步网络请求
        # cc=cn 代表中国区价格，l=zh-cn 代表中文
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc=cn&l=zh-cn"

        # 使用 async with 确保连接池高效率复用
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            try:
                logger.info(f"🌐 [Network Request] 正在异步请求 Steam 官方服务器: AppID={app_id}")
                response = await client.get(url)

                if response.status_code != 200:
                    raise HTTPException(status_code=502, detail=f"Steam 平台响应异常，状态码: {response.status_code}")

                data = response.json()

                # 3. 严格的数据边界防御
                if not data or str(app_id) not in data or not data[str(app_id)].get('success'):
                    raise HTTPException(status_code=404,
                                        detail="未找到该游戏，请检查 AppID 是否正确（部分锁区或下架游戏无法查询）")

                game_payload = data[str(app_id)]['data']

                # 4. 数据清洗与标准化转换
                name = game_payload.get('name', '未知游戏')
                is_free = game_payload.get('is_free', False)
                header_image = game_payload.get('header_image', '')  # 顺便把游戏封面图带给前端

                if is_free:
                    result = {
                        "name": name, "is_free": True, "header_image": header_image,
                        "currency": "CNY", "initial_price": "¥ 0.00", "current_price": "¥ 0.00", "discount_percent": 0
                    }
                else:
                    price_overview = game_payload.get('price_overview')
                    if not price_overview:
                        result = {
                            "name": name, "is_free": False, "header_image": header_image,
                            "currency": "CNY", "initial_price": "暂无", "current_price": "暂无", "discount_percent": 0
                        }
                    else:
                        result = {
                            "name": name,
                            "is_free": False,
                            "header_image": header_image,
                            "currency": price_overview.get('currency', 'CNY'),
                            "initial_price": price_overview.get('initial_formatted', ''),
                            "current_price": price_overview.get('final_formatted', ''),
                            "discount_percent": price_overview.get('discount_percent', 0)
                        }

                # 5. 写入缓存
                cls._CACHE[app_id] = {
                    "expire_at": current_time + cls._CACHE_TTL,
                    "data": result
                }
                return result

            except httpx.RequestError as exc:
                logger.error(f"❌ 请求 Steam 发生网络崩溃: {exc}")
                raise HTTPException(status_code=504, detail="连接 Steam 服务器超时，请稍后再试")