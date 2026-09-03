from telegram import Update
from telegram.ext import ContextTypes

from src.python_files.utils.decorators import logger

parola="macro"
@logger
async def start_command(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	if context.args:
		payload:str = context.args[0]
		await _handle_mini_app_data(update, payload)
		return
	else:
		reply:str = f"Benvenuto. Io sono il bot che ritiene che {parola} sia meglio."
	await update.message.reply_text(reply)


async def _handle_mini_app_data(update:Update, payload:str) -> None:
	await update.message.reply_text(f"Dati ricevuti dalla mini app: {payload}")
