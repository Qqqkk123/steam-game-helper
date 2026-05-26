from fastapi import APIRouter
from app.services.steam_api import SteamAPIService

router = APIRouter()

@router.get("/price/{app_id}")
async def get_game_price(app_id: str):
    """
    暴露给前端小程序的 API 接口
    使用 await 关键字强行挂起并等待异步服务层返回清洗完的 dict 数据
    """
    # ⚠️ 确保这里必须有 await 关键字！
    result = await SteamAPIService.fetch_game_price_by_id(app_id)
    return result