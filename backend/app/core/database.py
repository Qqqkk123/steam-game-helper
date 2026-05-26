from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 在 backend 目录下生成一个名为 steam_assistant.db 的本地数据库文件
DATABASE_URL = "sqlite:///./steam_assistant.db"

# 创建数据库引擎 (connect_args={"check_same_thread": False} 支持多线程异步并发)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 创建能生产数据库连接会话的工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 所有 ORM 模型类的基类
Base = declarative_base()

# 🛡️ 之前缺少的正是这个核心依赖注入函数！
def get_db():
    """
    FastAPI 专用的数据库会话依赖注入生成器。
    当接口收到网络请求时，它会自动打开一个数据库连接；
    当接口处理完毕把数据吐给小程序后，它会自动关闭连接，释放内存，性能极其优秀。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()