import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

# ⚠️ 升级为 steam_app
from steam_app.core.database import SessionLocal
from steam_app.models.game import UserSubscription
from steam_app.services.steam_api import SteamAPIService
# ... 下方代码完全保持不变

logger = logging.getLogger(__name__)


async def check_all_prices_job():
    """
    后台核心定时任务：定时遍历数据库中所有受监控的游戏，异步刷新价格并对比
    """
    logger.info("⏰ [Scheduler Task] 定时价格轮询任务已启动...")
    db: Session = SessionLocal()

    try:
        # 1. 找出数据库中所有被订阅的游戏（去重查询以减少 Steam 请求压力）
        subscriptions = db.query(UserSubscription).all()
        if not subscriptions:
            logger.info("📋 当前数据库中暂无监控游戏，跳过轮询。")
            return

        logger.info(f"🔍 准备检查 {len(subscriptions)} 个游戏的最新价格...")

        # 2. 遍历并利用 Sprint 1 的高性能异步客户端获取最新数据
        for sub in subscriptions:
            try:
                # 异步获取最新价格
                latest_data = await SteamAPIService.fetch_game_price_by_id(sub.app_id)

                current_price_str = latest_data.get("current_price", "")

                logger.info(f"🎮 检查游戏《{sub.game_name}》: 原始价={sub.initial_price} | 实时价={current_price_str}")

                # 3. 核心降价判定熔断器
                # 体验版先做字符串变动对比（如果最新价字符串和之前存的不一样，且不是暂无，说明价格变了）
                if current_price_str and current_price_str != sub.current_price:
                    logger.warning(f"🚨 [PRICE DROP DETECTION] 游戏《{sub.game_name}》价格发生变动！")

                    # 🌟 这里是未来触发邮件/微信通知的锚点：
                    # await send_price_drop_email(sub.game_name, sub.current_price, current_price_str)

                # 4. 更新数据库中的最新价格和更新时间
                sub.current_price = current_price_str
                db.commit()

            except Exception as e:
                logger.error(f"❌ 轮询游戏 AppID={sub.app_id} 价格时发生异常: {str(e)}")
                continue

    finally:
        db.close()
        logger.info("⏰ [Scheduler Task] 本轮价格轮询检查结束。")


# 初始化异步定时任务调度器
scheduler = AsyncIOScheduler()


def start_scheduler():
    """
    启动后台定时器，挂载轮询任务
    """
    # 为了方便你立刻看到效果，开发阶段我们设定为每 60 秒 (1分钟) 全自动轮询一次价格
    scheduler.add_job(check_all_prices_job, 'interval', seconds=60, id='steam_price_tracker')
    scheduler.start()
    logger.info("🚀 [Scheduler System] 后台异步定时监控系统成功上线！")