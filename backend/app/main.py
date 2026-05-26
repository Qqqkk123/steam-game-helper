import sys
import os

# ==================== 路径保护盾 ====================
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
# ====================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.v1.games import router as games_router
from app.core.database import engine, Base  # 🌟 新增：导入引擎和基类

# 🌟 新增：让 SQLAlchemy 检查并自动在本地磁盘创建所有缺失的数据库表
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Steam 游戏助手后端",
    description="Steam 游戏推荐及价格优惠提醒记录系统的后端 API",
    version="1.0.0"
)

# 🛡️ 企业级 CORS 跨域放行配置，打通微信小程序真机/模拟器双向通信
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 放行所有源，保证本地调试无网络阻碍
    allow_credentials=True,
    allow_methods=["*"],  # 放行所有 HTTP 动作 (GET, POST 等)
    allow_headers=["*"],
)

app.include_router(games_router, prefix="/api/v1/games", tags=["游戏接口"])

@app.get("/")
def root():
    return {"message": "Steam Game Helper API is running!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)