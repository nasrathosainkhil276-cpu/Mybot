import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import yt_dlp

# تنظیمات لاگ برای دیدن خطاها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ⚠️  Revoke گرفتید، اینجا 8907733631:AAHojHO_a7pNVt_RLEYn8J0ISdm-anwf4Nw دهید
BOT_TOKEN = "توکن_جدید_خود_را_اینجا_بگذارید"

# تنظیمات دانلودر
YDL_OPTIONS = {
    'format': 'best[ext=mp4]/best', # بهترین کیفیت MP4
    'outtmpl': 'downloads/%(title)s.%(ext)s', # محل ذخیره
    'noplaylist': True, # فقط یک ویدیو دانلود کن
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    # بررسی اینکه آیا پیام یک لینک است یا خیر
    if not url.startswith("http"):
        await update.message.reply_text("لطفاً یک لینک معتبر از یوتیوب، اینستاگرام، تیک‌تاک و... ارسال کنید.")
        return

    status_msg = await update.message.reply_text("⏳ در حال پردازش لینک... لطفاً صبر کنید.")

    # ایجاد پوشه دانلود در صورت نبود
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    try:
        # دانلود ویدیو با yt-dlp
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
        await status_msg.edit_text("📥 دانلود شد. در حال ارسال به تلگرام...")

        # بررسی حجم فایل (محدودیت تلگرام برای ربات‌ها 50 مگابایت است)
        file_size = os.path.getsize(filename) / (1024 * 1024) # تبدیل به مگابایت
        
        if file_size > 50:
            await status_msg.edit_text(f"⚠️ حجم ویدیو ({file_size:.1f} مگابایت) بیشتر از حد مجاز تلگرام (50MB) است. در حال فشرده‌سازی...")
            # در اینجا می‌توانید از FFmpeg برای فشرده‌سازی استفاده کنید، اما برای سادگی فعلاً ارسال نمی‌کنیم
            await update.message.reply_text("متأسفانه حجم فایل برای ارسال توسط ربات زیاد است.")
        else:
            # ارسال ویدیو به کاربر
            with open(filename, 'rb') as video:
                await update.message.reply_video(video=video, caption="✅ دانلود با موفقیت انجام شد.")
            
            await status_msg.delete() # حذف پیام وضعیت

    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text("❌ خطایی رخ داد. لطفاً مطمئن شوید لینک صحیح است و ویدیو خصوصی نیست.")
    
    finally:
        # پاک کردن فایل از سرور بعد از ارسال (برای جلوگیری از پر شدن حافظه)
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    print("ربات روشن شد...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # شنیدن پیام‌های متنی (لینک‌ها)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    application.add_handler(message_handler)
    
    # شروع ربات
    application.run_polling()
