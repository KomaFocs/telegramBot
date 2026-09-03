from telegram import Update
from telegram.ext import ContextTypes

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	error_msg:str = f"\nERROR\nUpdate {update} caused error {context.error}"
	await update.message.reply_text(error_msg)
	print(error_msg)
	return
