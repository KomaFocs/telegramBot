from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Update
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

async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    received_data = update.effective_message.web_app_data.data
    await update.message.reply_text(f"📩 Dati ricevuti dalla Mini App: {received_data}")