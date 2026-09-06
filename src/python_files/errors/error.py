from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from src.python_files.utils.constants import DIR, ERROR_CHAT

ERROR_FILE:Path = DIR.SECRETS / ERROR_CHAT
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	try:
		with open(ERROR_FILE, "r") as f:
			chat_id = f.read().strip()

		error_msg:str = f"\nERROR\nUpdate {update} caused error {context.error}"
		if not chat_id:
			print(error_msg)
		else:
			await context.bot.send_message(chat_id=chat_id, text=error_msg)
	except Exception as e:
		print(e)
