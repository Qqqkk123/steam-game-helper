from sqlalchemy import Column, Integer, String, Float, DateTime
# ⚠️ 升级为 steam_app
from steam_app.core.database import Base
import datetime
# ... 下方代码完全保持不变

class UserSubscription(Base):
    """
    用户游戏降价监控订阅表 (ORM 模型)
    ⚠️ 必须确保类名叫 UserSubscription，且继承自 Base
    """
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), index=True, default="default_user")  # 微信用户标识
    app_id = Column(String(20), index=True, nullable=False)
    game_name = Column(String(200), nullable=False)
    cover_image = Column(String(500))

    initial_price = Column(String(50))  # 收藏时的价格
    current_price = Column(String(50))  # 当前实时价格
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)