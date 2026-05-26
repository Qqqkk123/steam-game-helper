import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib

logger = logging.getLogger(__name__)

# 🔒 邮箱配置配置中心 (开发阶段先写在这里，后续可移入 config.py)
# 💡 提示：推荐使用 QQ 邮箱、163 邮箱或 Gmail
SMTP_SERVER = "smtp.qq.com"  # 如果是网易是 smtp.163.com
SMTP_PORT = 465  # SSL 加密端口
SMTP_USER = "2784680097@qq.com"  # 你的发件人邮箱
SMTP_PASSWORD = "hpkyesetgfqgdeib"  # ⚠️ 注意：不是邮箱登录密码，是邮箱后台开启 SMTP 后生成的「授权码」
RECEIVER_EMAIL = "2784680097@qq.com"  # 接收降价提醒的邮箱（也可以和发件人是同一个）


class NotifierService:
    @staticmethod
    async def send_price_drop_email(game_name: str, old_price: str, new_price: str, cover_image: str, app_id: str):
        """
        利用 aiosmtplib 异步发送极其精美的 Steam 暗黑风降价提醒 HTML 邮件
        """
        if SMTP_USER == "你的邮箱@qq.com" or SMTP_PASSWORD == "你的授权码":
            logger.warning("⚠️ [Notifier] 检测到邮件服务未配置真实的账号密码，跳过发送推送。")
            return

        # 1. 组装复杂的邮件报文结构
        message = MIMEMultipart("alternative")
        # ⚠️ 彻底绝杀 550 报错：不要带任何中文别名和尖括号，直接填入纯邮箱变量！
        message["From"] = SMTP_USER
        message["To"] = RECEIVER_EMAIL
        message["Subject"] = f"🚨 降价预警！您监控的游戏《{game_name}》打折啦！"

        # 2. 纯手写 Steam 科技暗黑风精美 HTML 模板
        html_content = f"""
        <html>
        <body style="background-color: #1b2838; font-family: 'Segoe UI', Helvetica, Arial, sans-serif; padding: 20px; color: #ffffff;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #121a24; border: 1px solid #233c51; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
                <div style="background: linear-gradient(to right, #1a7cc7, #47bfff); padding: 20px; text-align: center;">
                    <h2 style="margin: 0; color: #ffffff; font-size: 24px; letter-spacing: 1px;">🎮 Steam 降价雷达</h2>
                </div>
                <img src="{cover_image}" style="width: 100%; max-height: 250px; object-fit: cover;" alt="Game Cover" />
                <div style="padding: 30px;">
                    <p style="font-size: 16px; color: #66c0f4; margin-top: 0;">尊敬的小程序主：</p>
                    <p style="font-size: 16px; line-height: 1.6;">您在监控记录本中关注的游戏 <strong style="font-size: 18px; color: #ffffff;">《{game_name}》</strong> 刚刚价格发生了变动！</p>

                    <div style="background-color: #0d131b; border: 1px solid #2a475e; border-radius: 6px; padding: 20px; margin: 25px 0; display: flex; text-align: center;">
                        <div style="flex: 1; border-right: 1px solid #233c51; padding: 0 10px;">
                            <span style="font-size: 13px; color: #626e7a; display: block; margin-bottom: 5px;">原记录价格</span>
                            <span style="font-size: 18px; color: #889296; text-decoration: line-through;">{old_price}</span>
                        </div>
                        <div style="flex: 1; padding: 0 10px;">
                            <span style="font-size: 13px; color: #a3d200; display: block; margin-bottom: 5px;">🔥 当前突降价</span>
                            <span style="font-size: 22px; color: #a3d200; font-weight: bold;">{new_price}</span>
                        </div>
                    </div>

                    <div style="text-align: center; margin-top: 30px;">
                        <a href="https://store.steampowered.com/app/{app_id}" style="background-color: #618524; color: #9be61a; padding: 12px 30px; font-size: 16px; font-weight: bold; text-decoration: none; border-radius: 4px; border: 1px solid #82b432; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                            🛒 立即前往 Steam 商店割韭菜
                        </a>
                    </div>
                </div>
                <div style="background-color: #080d13; padding: 15px; text-align: center; font-size: 12px; color: #4a535a; border-top: 1px solid #10171f;">
                    本邮件由您的本地 Python 后端服务器全自动监测并发送。
                </div>
            </div>
        </body>
        </html>
        """

        # 3. 注入 HTML 内容到邮件
        part = MIMEText(html_content, "html", "utf-8")
        message.attach(part)

        try:
            # 4. 异步连接邮件服务器发送
            logger.info(f"📧 [Mail System] 正在建立异步安全连接并准备发送邮件...")
            async with aiosmtplib.SMTP(hostname=SMTP_SERVER, port=SMTP_PORT, use_tls=True) as smtp:
                await smtp.login(SMTP_USER, SMTP_PASSWORD)
                await smtp.send_message(message)
            logger.info(f"🎉 [Mail System] 降价预警邮件已成功送达您的手机邮箱！")
        except Exception as e:
            logger.error(f"❌ [Mail System] 邮件发送失败，请检查配置或授权码: {str(e)}")