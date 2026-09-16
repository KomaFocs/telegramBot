import random
from telegram.constants import ChatAction, ChatType
from telegram.ext import ContextTypes
from telegram import Update, Message
from src.python_files.utils.constants import PAROLA

def _log(message:str) -> None:
	print(message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	if not update.message: return  # messaggio non valido / modifica / callback

	message:Message = update.message
	msg_type:str = message.chat.type
	message_text:str = message.text or message.caption or ""
	message_string:str = message_text.lower()
	bot_username:str = context.bot.username or ""
	is_group:bool = message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)
	user_id:int
	name:str
	print(f"group={is_group}, message={message_string}, chatid={update.effective_chat.id}")
	if is_group and bot_username.lower() not in message_string:
		return  # messaggio ricevuto in un gruppo, ma senza venire interpellato

	# Da qui in poi il messaggio è privato o è in un gruppo ma diretto al bot

	await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
	if message.from_user:
		user_id = message.from_user.id
		name = message.from_user.first_name

	elif message.sender_chat:
		user_id = message.sender_chat.id
		name = message.sender_chat.title

	else:
		user_id = 0
		name = "Ignoto"

	if msg_type in [ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP]:
		_log(f"[{user_id} {name}]: {message_string}")

	meglio_macro:str = "Sì ok, micro... ma Meglio Macro."
	risposte:list[str] = ["bravo", "ottimo", "eccellente", "spettacolare", "giusto", "ben detto", "decisamente valido", "basato"]

	if PAROLA in message_string:
		response = random.choice(risposte)
	elif "micro" in message_string:
		response = meglio_macro
	else:
		response = f"errore. non c'è \"{PAROLA}\" nel messaggio.".upper()

	_log(f"[{context.bot.username}]: {response}")

	await message.reply_text(text=response, reply_to_message_id=message.message_id)
