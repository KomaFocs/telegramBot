import traceback
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes
from src.python_files.utils.constants import DIR
from src.python_files.utils.decorators import error_origin

@error_origin()
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	_ERROR_CHAT:Path = DIR.GROUP_TEST

	with open(_ERROR_CHAT, "r") as f:
		error_chat_id = f.read().strip()
		error_msg:str = f"ERROR\nUpdate {update} caused error {context.error}"

	try:
		if not error_chat_id:
			print(error_msg)
		else:
			await context.bot.send_message(chat_id=error_chat_id, text=error_msg)
			traceback.print_exception(
				type(context.error),
				context.error,
				context.error.__traceback__
			)
	except Exception as e:
		print(e)


