from src.python_files.utils.decorators import logger, single_execution, chat_action
from telegram import Update
from telegram.ext import ContextTypes

@logger
@single_execution()
@chat_action()
async def submissions_command(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	await update.message.reply_text("Ancora non implementato.")
