from telegram import Update
from telegram.ext import ContextTypes

from src.python_files.utils.decorators import logger

parola="macro"
@logger
async def start_command(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	reply: str = f"Benvenuto. Io sono il bot che ritiene che {parola} sia meglio."
	await update.message.reply_text(reply)
