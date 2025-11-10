import os
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- تنظیمات لاگ‌گیری ---
# این بار لاگ‌گیری را در سطح بالا انجام می‌دهیم تا همه چیز را ثبت کند
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- خواندن متغیرهای محرمانه ---
# اینها را از Vercel می‌خوانیم
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID')

# --- توابع ربات ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پاسخ به دستور /start"""
    user_id = update.message.from_user.id
    logger.info(f"User {user_id} started the bot.") # اضافه کردن لاگ برای تست
    
    # مقایسه ادمین آیدی
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

    # --- ثبت دستورات ---
    application.add_handler(CommandHandler("start", start))
    
    # (بقیه دستورات در آینده اینجا اضافه می‌شوند)

    return application

# --- تابع اصلی Vercel (اصلاح شده) ---

async def handler(event, context):
    """تابع اصلی هندلر برای Vercel با مدیریت خطای صحیح"""
    
    try:
        # **اصلاح کلیدی:** راه‌اندازی ربات *داخل* بلوک try قرار گرفت
        application = await setup_bot()
        
        # پردازش درخواست تلگرام
        body = json.loads(event['body'])
        update = Update.de_json(body, application.bot)
        
        await application.process_update(update)
        
        # پاسخ موفقیت آمیز
        return {'statusCode': 200, 'body': 'Success'}
        
    except Exception as e:
        # **اصلاح کلیدی:** حالا هر خطایی (از جمله خطای راه‌اندازی) در لاگ ثبت می‌شود
        logger.error(f"!!! خطای اساسی در هندلر !!!: {e}", exc_info=True)
        
        # پاسخ خطا
        return {'statusCode': 500, 'body': 'Internal Server Error'}
