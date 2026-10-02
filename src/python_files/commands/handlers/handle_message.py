import asyncio
import random

from telegram import Message as TelegramMessage, Update
from telegram.constants import ChatAction, ChatType
from telegram.ext import ContextTypes

from src.python_files.models.dao.submission_dao import SubmissionDAO
from src.python_files.utils.constants import PAROLA, DIR
from src.python_files.utils.filters import get_from_file


def _log(message: str) -> None:
	print(message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	if not update.message:
		return

	message: TelegramMessage = update.message
	msg_type: str = message.chat.type
	message_text: str = message.text or message.caption or ""
	message_string: str = message_text.lower()
	bot_username: str = (context.bot.username or "").lower()
	is_group: bool = msg_type in (ChatType.GROUP, ChatType.SUPERGROUP)

	if is_group and bot_username not in message_string:
		return  # messaggio ricevuto in un gruppo, ma senza menzionare il bot

	await context.bot.send_chat_action(
		chat_id=update.effective_chat.id,
		action=ChatAction.TYPING
	)

	if message.from_user:
		user_id = message.from_user.id
		name = message.from_user.first_name
	elif message.sender_chat:
		user_id = message.sender_chat.id
		name = message.sender_chat.title
	else:
		user_id = 0
		name = "Ignoto"

	if msg_type in (ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP):
		_log(f"[{user_id} {name}]: {message_string}")

	meglio_macro: str = "Sì ok, micro... ma Meglio Macro."
	risposte: list[str] = [
		"bravo", "ottimo", "eccellente", "spettacolare",
		"giusto", "ben detto", "decisamente valido", "basato"
	]

	response:str = "Sono senza parole"

	if PAROLA in message_string:
		response = random.choice(risposte)
	elif "micro" in message_string:
		response = meglio_macro
	elif "reset" == message_string:
		user_id = str(update.effective_user.id)
		allowed_ids = get_from_file(DIR.SECRETS / "id.txt")
		if user_id not in allowed_ids:
			return
		SubmissionDAO.reset_pending_group_submissions()
	else:
		response = f"errore. non c'è \"{PAROLA}\" nel messaggio.".upper()

	_log(f"[{context.bot.username}]: {response}")

	await asyncio.sleep(random.uniform(1,3))

	await message.reply_text(
		text=response,
		reply_to_message_id=message.message_id
	)

