import sys
import os

# ==================== 动态路径保护盾 ====================
current_dir = os.path.dirname(os.path.abspath(__file__)) # steam_app 目录
backend_dir = os.path.dirname(current_dir)               # backend 目录
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
# ====================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# ⚠️ 注意：全部对齐升级为新专有包名 steam_app
from steam_app.api.v1.games import router as games_router
from steam_app.core.database import engine, Base
from steam_app.tasks.scheduler import start_scheduler, scheduler

# 自动创建数据库表
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(title="Steam Game Helper API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games_router, prefix="/api/v1/games", tags=["games"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Steam Game Helper API"}

if __name__ == "__main__":
    import uvicorn
    # ⚠️ 这里的模块字符串也要同步修改为 steam_app.main
    uvicorn.run("steam_app.main:app", host="127.0.0.1", port=8000, reload=False)