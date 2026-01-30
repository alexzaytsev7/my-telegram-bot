# bot.py
import os
import tempfile
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import httpx

# === Настройки ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")

async def start(update, context):
    await update.message.reply_text("Привет! Я работаю в облаке 🌥️")
    
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    
    # Скачиваем OGG-файл
    file = await context.bot.get_file(voice.file_id)
    
    with tempfile.NamedTemporaryFile(suffix=".ogg") as tmp_ogg:
        await file.download_to_drive(tmp_ogg.name)
        
        # Читаем аудио
        with open(tmp_ogg.name, "rb") as f:
            audio_data = f.read()
        
        # Отправляем в Yandex SpeechKit
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
                    headers={"Authorization": f"Api-Key {YANDEX_API_KEY}"},
                    content=audio_data,
                    params={
                        "lang": "ru-RU",      # Русский язык
                        "format": "oggopus",  # Формат от Telegram
                        "sampleRateHertz": 48000
                    }
                )
                result = response.json()
                text = result.get("result", "").strip()
                
                if not text:
                    await update.message.reply_text("Не удалось распознать речь.")
                    return
                
                await update.message.reply_text(f"Вы сказали: *{text}*", parse_mode="Markdown")
                
                # === Опционально: отправить в LLM ===
                # answer = await ask_llm(text)
                # await update.message.reply_text(answer)
                
            except Exception as e:
                await update.message.reply_text(f"Ошибка транскрибации: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.run_polling()

if __name__ == "__main__":
    main()

