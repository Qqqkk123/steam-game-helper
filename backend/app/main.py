import sys
import os

# ==================== 路径保护盾 ====================
# 获取当前 main.py 文件所在的目录（即 app 目录）
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取 app 目录的上一级目录（即 backend 目录）
backend_dir = os.path.dirname(current_dir)

# 将这两个路径都强行加入到 Python 的系统搜索路径中
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
# ====================================================

from fastapi import FastAPI
import uvicorn
# 此时无论你在哪个目录下运行，下面的导入都能完美识别
from app.api.v1.games import router as games_router

# 初始化 FastAPI 实例
app = FastAPI(
    title="Steam 游戏助手后端",
    description="Steam 游戏推荐及价格优惠提醒记录系统的后端 API",
    version="1.0.0"
)

# 注册路由模块，并加上统一前缀 v1
app.include_router(games_router, prefix="/api/v1/games", tags=["游戏接口"])

@app.get("/")
def root():
    return {"message": "Steam Game Helper API is running!"}

if __name__ == "__main__":
    # 使用字符串形式启动，配合 reload=True 实现热重载（改动代码自动刷新）
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)