from telegram import Update
from telegram.ext import ContextTypes

from src.python_files.utils.decorators import logger, chat_action
from src.python_files.utils.util import PAROLA


@logger
@chat_action()
async def meglio_command(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	await update.message.reply_text(f"{PAROLA}.")

