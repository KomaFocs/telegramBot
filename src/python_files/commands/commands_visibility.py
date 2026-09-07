from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from src.python_files.config.lista_comandi import Nome_Comandi
from src.python_files.utils.constants import CHATS_FILE, DIR

_ADMIN_COMMANDS:list[str] = [Nome_Comandi.SUBMISSIONS, Nome_Comandi.START]
async def visibility(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	message = update.effective_message

	if not message or not message.text or not message.text.startswith('/'):
		return

	chat = update.effective_chat
	user = update.effective_user

	if not chat or not user:
		raise ApplicationHandlerStop

	with open(DIR.SECRETS/CHATS_FILE) as file:
		chat_ids:list[str] = file.readlines()[0].strip().split("___")
		#
		megliomacro = int(3)

	if chat.id != megliomacro:
		return

	command = message.text.split()[0].removeprefix("/")
	if command not in _ADMIN_COMMANDS:
		return

	member = await context.bot.get_chat_member(megliomacro, user.id)
	if member.status not in ("administrator", "creator"):
		raise ApplicationHandlerStop