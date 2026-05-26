from fastapi import APIRouter
from app.services.steam_api import SteamAPIService

# 创建游戏模块的路由实例
router = APIRouter()

@router.get("/price/{app_id}")
def get_game_price(app_id: str):
    """
    暴露给前端小程序的 API 接口：获取 Steam 游戏价格
    """
    # 路由层不写具体抓取逻辑，直接调用服务层，符合解耦规范
    return SteamAPIService.fetch_game_price_by_id(app_id)