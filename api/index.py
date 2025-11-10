import os
import json
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, Dispatcher, CallbackContext

# --- تنظیمات لاگ‌گیری ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- خواندن متغیرهای محرمانه ---
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID')

# --- توابع ربات (نسخه همگام) ---
def start(update: Update, context: CallbackContext) -> None:
    """پاسخ به دستور /start"""
    try:
        user_id = update.message.from_user.id
        logger.info(f"User {user_id} started the (sync) bot.")
        
        if str(user_id) == str(ADMIN_USER_ID):
            update.message.reply_text('>> تست ادمین: ربات همگام (Sync) کار کرد! <<')
        else:
            update.message.reply_text('>> تست کاربر: ربات همگام (Sync) کار کرد! <<')
            
    except Exception as e:
        logger.error(f"Error in start command: {e}", exc_info=True)

# --- تابع اصلی Vercel (نسخه همگام) ---
def handler(event, context):
    """تابع اصلی هندلر برای Vercel"""
    
    # ما باید مدیریت خطا را در بالاترین سطح قرار دهیم
    try:
        if not TOKEN:
            logger.critical("BOT_TOKEN پیدا نشد!")
            # اگر توکن نباشد، به تلگرام خطا برمی‌گردانیم تا دوباره تلاش نکند
            return {'statusCode': 200, 'body': 'Bot token not configured.'}
        
        # راه‌اندازی ربات با استفاده از نسخه 13
        updater = Updater(token=TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        # ثبت دستورات
        dispatcher.add_handler(CommandHandler("start", start))

        # پردازش درخواست
        body = json.loads(event['body'])
        update = Update.de_json(body, updater.bot)
        
        dispatcher.process_update(update)
        
        # پاسخ موفقیت آمیز
        return {'statusCode': 200, 'body': 'Success'}
        
    except Exception as e:
        # اگر هر خطای دیگری رخ دهد، آن را لاگ می‌کنیم
        logger.error(f"!!! HANDLER CRASH (SYNC) !!!: {e}", exc_info=True)
        return {'statusCode': 500, 'body': 'Internal Server Error'}
