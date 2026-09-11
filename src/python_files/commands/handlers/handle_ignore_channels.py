from telegram import Update, Chat
from telegram.ext import ContextTypes, ApplicationHandlerStop


async def ignora_canali(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	chat:Chat = update.effective_chat
	if chat is None:
		return

	if chat.type == "channel":
		raise ApplicationHandlerStop
