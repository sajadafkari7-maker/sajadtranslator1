import os
import json
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- تنظیمات لاگ‌گیری ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- خواندن متغیرهای محرمانه ---
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID')

# --- توابع ربات (نسخه ساده شده) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    logger.info(f"User {user_id} started the (minimal) bot.")
    
    # ما فقط می‌خواهیم ببینیم آیا این پیام ارسال می‌شود یا خیر
    if str(user_id) == str(ADMIN_USER_ID):
        await update.message.reply_text('>> تست ادمین: ربات ساده کار کرد! <<')
    else:
        await update.message.reply_text('>> تست کاربر: ربات ساده کار کرد! <<')

async def setup_bot():
    """راه‌اندازی ربات (نسخه ساده شده)"""
    if not TOKEN:
        logger.critical("BOT_TOKEN پیدا نشد!")
        raise ValueError("BOT_TOKEN not found.")
        
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    return application

# --- تابع اصلی Vercel (بدون تغییر) ---
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
            # اگر این بار هم کرش کند، خطا 100% اینجا ثبت می‌شود
            logger.error(f"!!! HANDLER CRASH !!!: {e}", exc_info=True)
            return {'statusCode': 500, 'body': 'Internal Server Error'}

    return asyncio.run(async_main())
