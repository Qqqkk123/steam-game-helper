from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# ⚠️ 升级为 steam_app
from steam_app.services.steam_api import SteamAPIService
from steam_app.core.database import get_db
from steam_app.models.game import UserSubscription
from steam_app.schemas.game import SubscriptionCreate, SubscriptionResponse

router = APIRouter()


# --- 1. 保留原本的实时查询接口 ---
@router.get("/price/{app_id}")
async def get_game_price(app_id: str):
    return await SteamAPIService.fetch_game_price_by_id(app_id)


# --- 2. 新增：一键移入降价提醒监控本 (写入数据库) ---
@router.post("/subscribe", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def subscribe_game(payload: SubscriptionCreate, db: Session = Depends(get_db)):
    """
    接收前端传递的游戏数据，写入 SQLite 本地数据库
    Depends(get_db) 实现了企业级的连接池依赖注入
    """
    # 状态防御：防止用户重复订阅同一款游戏
    exists = db.query(UserSubscription).filter(
        UserSubscription.user_id == "default_user",
        UserSubscription.app_id == payload.app_id
    ).first()

    if exists:
        raise HTTPException(
            status_code=400,
            detail=f"游戏《{payload.game_name}》已经在您的降价监控本里了，无需重复添加！"
        )

    # 将 Pydantic 校验后的数据转换为 ORM 实体对象
    new_sub = UserSubscription(
        user_id="default_user",  # 体验版先采用默认用户
        app_id=payload.app_id,
        game_name=payload.game_name,
        cover_image=payload.cover_image,
        initial_price=payload.initial_price,
        current_price=payload.current_price
    )

    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)  # 刷新以获取自增的 ID 和时间戳
    return new_sub


# --- 3. 新增：获取用户当前的监控本列表 (从数据库读取) ---
@router.get("/watchlist", response_model=List[SubscriptionResponse])
def get_watchlist(db: Session = Depends(get_db)):
    """
    拉取本地数据库中存储的所有受监控游戏列表
    """
    watchlist = db.query(UserSubscription).filter(UserSubscription.user_id == "default_user").all()
    return watchlist