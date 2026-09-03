from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes, CommandHandler, Application

WEB_APP_URL = "https://komafocs.github.io/telegramBot/"

async def open_app(update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text="🚀 Apri Mini App",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )]
    ])
    await update.message.reply_text(
        "Clicca sul pulsante qui sotto per avviare l'app:",
        reply_markup=keyboard
    )
