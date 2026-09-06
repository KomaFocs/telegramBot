from telegram import Update
from telegram.ext import ContextTypes

from src.python_files.services.mini_app_service import is_valid_mini_app_payload, handle_mini_app_payload
from src.python_files.utils.constants import PAROLA
from src.python_files.utils.decorators import logger

@logger
async def start_command(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	payload:str = context.args[0] if context.args else None

	if is_valid_mini_app_payload(payload):
		await handle_mini_app_payload(update=update, context=context, payload=payload)
	else:
		reply:str = f"Benvenuto. Io sono il bot che ritiene che {PAROLA} sia meglio."
		await update.message.reply_text(reply)
