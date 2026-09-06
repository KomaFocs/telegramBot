from telegram import Update
from telegram.ext import ContextTypes

from src.python_files.utils.constants import MINI_APP_PREFIX
from src.python_files.utils.decorators import chat_action


def is_valid_mini_app_payload(payload:str|None) -> bool:
	if not payload:
		return False

	return payload.startswith(MINI_APP_PREFIX) and len(payload) > len(MINI_APP_PREFIX)


@chat_action()
async def handle_mini_app_payload(update:Update, context:ContextTypes.DEFAULT_TYPE, payload:str|None) -> None:
	if update.message:
		try:
			await update.message.delete()
		except Exception:
			pass

	clean_data:str = payload.removeprefix(MINI_APP_PREFIX)
	await update.message.reply_text(f"Ho ricevuto dati dalla mini app: {clean_data}")