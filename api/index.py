import os
import json
import logging
import asyncio # <--- (اضافه شدن کتابخانه جدید)
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- تنظیمات لاگ‌گیری ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- خواندن متغیرهای محرمانه ---
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID')

# --- توابع ربات ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پاسخ به دستور /start"""
    user_id = update.message.from_user.id
    logger.info(f"User {user_id} started the bot.")
    
    if str(user_id) == str(ADMIN_USER_ID):
        await update.message.reply_text(
            'سلام ادمین! به پنل مدیریت خوش آمدید. برای نمایش دستورات /admin را بزنید.'
        )
    else:
        await update.message.reply_text(
            'سلام! من ربات مترجم فارسی/اسپانیایی هستم. '
            'لطفاً متن، صدا یا عکسی را برای ترجمه ارسال کنید.'
        )

async def setup_bot():
    """راه‌اندازی و مقداردهی اولیه ربات"""
    if not TOKEN:
        logger.critical("متغیر BOT_TOKEN پیدا نشد!")
        raise ValueError("BOT_TOKEN یافت نشد. لطفاً متغیرهای Vercel را چک کنید.")
        
    if not ADMIN_USER_ID:
        logger.warning("متغیر ADMIN_USER_ID پیدا نشد! (پنل ادمین کار نخواهد کرد)")

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    return application

# --- تابع اصلی Vercel (اصلاح نهایی) ---

# *** این اصلاح اصلی است: تابع از "async def" به "def" تغییر کرد ***
def handler(event, context):
    """تابع اصلی هندلر برای Vercel (به صورت همگام)"""
    
    async def async_main():
        """یک تابع داخلی ناهمزمان برای اجرای منطق ربات"""
        try:
            application = await setup_bot()
            
            body = json.loads(event['body'])
            update = Update.de_json(body, application.bot)
            
            await application.process_update(update)
            
            return {'statusCode': 200, 'body': 'Success'}
            
        except Exception as e:
            logger.error(f"!!! خطای اساسی در هندلر !!!: {e}", exc_info=True)
            return {'statusCode': 500, 'body': 'Internal Server Error'}

    # *** این بخش کلیدی است: ما تابع ناهمزمان را از درون تابع همگام اجرا می‌کنیم ***
    return asyncio.run(async_main())
