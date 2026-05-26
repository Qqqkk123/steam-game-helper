import requests
from fastapi import HTTPException


class SteamAPIService:
    @staticmethod
    def fetch_game_price_by_id(app_id: str) -> dict:
        """
        核心业务逻辑：专门负责向 Steam 服务器请求指定 app_id 的价格与折扣数据
        """
        # Steam 官方商品详情接口 (cc=cn 获取中国区价格)
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc=cn&l=zh-cn"

        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            # 校验 Steam 接口是否成功返回该游戏
            if not data or not data.get(app_id) or not data[app_id].get('success'):
                raise HTTPException(status_code=404, detail="未找到该游戏信息，请检查 AppID 是否正确")

            game_data = data[app_id]['data']
            name = game_data.get('name', '未知游戏')
            is_free = game_data.get('is_free', False)

            if is_free:
                return {"name": name, "is_free": True, "price_info": "免费"}

            price_overview = game_data.get('price_overview')
            if not price_overview:
                return {"name": name, "is_free": False, "price_info": "暂无价格信息"}

            # 返回精简后的标准化数据给上层路由
            return {
                "name": name,
                "is_free": False,
                "currency": price_overview.get('currency', 'CNY'),
                "initial_price": price_overview.get('initial_formatted', ''),
                "current_price": price_overview.get('final_formatted', ''),
                "discount_percent": price_overview.get('discount_percent', 0)
            }

        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"请求 Steam 接口失败: {str(e)}")