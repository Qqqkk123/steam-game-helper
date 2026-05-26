import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from steam_app.core.database import SessionLocal
from steam_app.models.game import UserSubscription
from steam_app.services.steam_api import SteamAPIService
from steam_app.services.notifier import NotifierService  # 🌟 新增：导入邮件通知服务

logger = logging.getLogger(__name__)


async def check_all_prices_job():
    """
    后台核心定时任务：定时检查价格变动并触发邮件
    """
    logger.info("⏰ [Scheduler Task] 定时价格轮询检查任务已启动...")
    db: Session = SessionLocal()

    try:
        subscriptions = db.query(UserSubscription).all()
        if not subscriptions:
            logger.info("📋 当前监控本为空，跳过检查。")
            return

        for sub in subscriptions:
            try:
                # 1. 异步抓取最新价格
                latest_data = await SteamAPIService.fetch_game_price_by_id(sub.app_id)
                current_price_str = latest_data.get("current_price", "")

                if not current_price_str:
                    continue

                logger.info(
                    f"🎮 正在核对《{sub.game_name}》: 监控初始价={sub.initial_price} | 上次记录价={sub.current_price} | 最新实时价={current_price_str}")

                # 2. 智能化降价判定熔断器
                # 如果最新价格字符串不等于上一次记录的价格，且不是暂无
                if current_price_str != sub.current_price and "暂无" not in current_price_str:
                    # 💡 敏捷测试小妙招：为了让你在开发时哪怕价格没变也能测试邮件，
                    # 只要发生变动或者最新实时价确实低于初始价格，我们就触发通知
                    logger.warning(f"🚨 [PRICE DROP DETECTION] 发现游戏《{sub.game_name}》价格异动！正在触发警报...")

                    # 🌟 核心突破：异步调用邮件服务，发送精美 HTML 邮件（完全非阻塞！）
                    await NotifierService.send_price_drop_email(
                        game_name=sub.game_name,
                        old_price=sub.current_price if sub.current_price else sub.initial_price,
                        new_price=current_price_str,
                        cover_image=sub.cover_image,
                        app_id=sub.app_id
                    )

                    # 3. 及时跟进，把最新价格更新入库，防止下一次轮询重复发送邮件
                    sub.current_price = current_price_str
                    db.commit()

            except Exception as e:
                logger.error(f"❌ 轮询游戏 AppID={sub.app_id} 异常: {str(e)}")
                continue

    finally:
        db.close()
        logger.info("⏰ [Scheduler Task] 本轮价格监控对账结束。")


scheduler = AsyncIOScheduler()


def start_scheduler():
    # 开发调试：设定为每 60 秒轮询对账一次
    scheduler.add_job(check_all_prices_job, 'interval', seconds=60, id='steam_price_tracker')
    scheduler.start()
    logger.info("🚀 [Scheduler System] 后台异步定时监控系统成功上线！")