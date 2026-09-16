from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from src.python_files.config.lista_comandi import Nome_Comandi
from src.python_files.utils.constants import DIR

_ADMIN_COMMANDS:list[str] = [Nome_Comandi.SUBMISSIONS, Nome_Comandi.START]
_ADMIN:str = "administrator"
_CREATOR:str = "creator"

async def visibility(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	message = update.effective_message

	if not message or not message.text or not message.text.startswith('/'):
		return

	chat = update.effective_chat
	user = update.effective_user

	if not chat or not user:
		raise ApplicationHandlerStop

	files = [DIR.GROUP_MEGLIOMACRO, DIR.CHANNEL_MACROMICROITALIA]
	channel_and_group_ids = []
	for file in files:
		with open(file, "r") as f:
			channel_and_group_ids.append(int(f.read().strip()))

	if chat.id not in channel_and_group_ids:
		return

	command = message.text.split()[0].removeprefix("/")
	if command not in _ADMIN_COMMANDS:
		return

	member = await context.bot.get_chat_member(channel_and_group_ids[1], user.id)
	if member.status not in (_ADMIN, _CREATOR):
		raise ApplicationHandlerStop