from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 微信前端往后端发送“添加关注”时，必须携带的数据格式校验
class SubscriptionCreate(BaseModel):
    app_id: str
    game_name: str
    cover_image: Optional[str] = ""
    initial_price: Optional[str] = ""
    current_price: Optional[str] = ""

# 后端吐给前端的规范数据格式
class SubscriptionResponse(BaseModel):
    id: int
    user_id: str
    app_id: str
    game_name: str
    cover_image: Optional[str]
    initial_price: Optional[str]
    current_price: Optional[str]
    last_updated: datetime

    class Config:
        from_attributes = True  # 允许 Pydantic 直接读取 SQLAlchemy 的 ORM 对象