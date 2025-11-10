import os
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# فعال کردن لاگ‌گیری (برای خطایابی)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(name)

# خواندن متغیرهای محرمانه از Vercel
# ما اینها را بعداً در Vercel تنظیم خواهیم کرد
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_USER_ID')

# تابع برای دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پاسخ به دستور /start"""
    user_id = update.message.from_user.id
    
    # بررسی اینکه آیا کاربر، ادمین است یا نه
    if str(user_id) == ADMIN_ID:
        await update.message.reply_text(
            'سلام ادمین! به پنل مدیریت خوش آمدید. برای نمایش دستورات /admin را بزنید.'
        )
    else:
        await update.message.reply_text(
            'سلام! من ربات مترجم فارسی/اسپانیایی هستم. '
            'لطفاً متن، صدا یا عکسی را برای ترجمه ارسال کنید.'
        )

# تابع اصلی که توسط Vercel اجرا می‌شود
async def setup_bot():
    """راه‌اندازی و مقداردهی اولیه ربات"""
    # ساخت اپلیکیشن ربات با توکن
    application = Application.builder().token(TOKEN).build()

    # --- ثبت دستورات ---
    # 1. دستور /start
    application.add_handler(CommandHandler("start", start))
    
    # (بقیه دستورات مثل ترجمه متن، صوت و پنل ادمین در اینجا اضافه خواهند شد)

    return application

# این بخش اصلی برای اتصال به Vercel (Serverless Function) است
# ما به جای "run_polling" از "webhook" استفاده می‌کنیم
# Vercel این تابع را به عنوان نقطه ورودی می‌شناسد
async def handler(event, context):
    """تابع اصلی هندلر برای Vercel"""
    # اول ربات را راه‌اندازی می‌کنیم
    application = await setup_bot()
    
    try:
        # درخواست دریافتی از Vercel را به JSON تبدیل می‌کنیم
        body = json.loads(event['body'])
        update = Update.de_json(body, application.bot)
        
        # آپدیت را پردازش می‌کنیم (اینجا تلگرام کارش را انجام می‌دهد)
        await application.process_update(update)
        
        # پاسخ موفقیت آمیز به Vercel
        return {'statusCode': 200, 'body': 'Success'}
        
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        # پاسخ خطا به Vercel
        return {'statusCode': 500, 'body': 'Internal Server Error'}
