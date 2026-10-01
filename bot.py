import os
import io
import logging
from threading import Thread

from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from huggingface_hub import InferenceClient

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]
HF_TOKEN = os.environ["HF_TOKEN"]

client = InferenceClient(api_key=HF_TOKEN)

web_app = Flask(__name__)


@web_app.route("/")
def home():
    return "AI Image Bot is running!"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Mujhe image ka prompt bhejo.\n\n"
        "Example:\n"
        "A futuristic city at night, cinematic, ultra realistic"
    )


async def generate_image(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    prompt = update.message.text

    msg = await update.message.reply_text(
        "🎨 Image generate ho rahi hai..."
    )

    try:
        image = client.text_to_image(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell"
        )

        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        await update.message.reply_photo(
            photo=image_bytes,
            caption="✨ AI Generated"
        )

        await msg.delete()

    except Exception:
        logging.exception("Generation error")
        await msg.edit_text(
            "❌ Image generate nahi ho payi. Please try again."
        )


def main():

    Thread(
        target=run_web,
        daemon=True
    ).start()

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            generate_image
        )
    )

    print("Bot is starting...")

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
