from telegram import Update
from telegram.ext import ContextTypes

async def handle_sticker(update:Update, context:ContextTypes.DEFAULT_TYPE):
        if update.message and update.message.sticker:
            print(f"[STICKER ID]: {update.message.sticker.file_id}")