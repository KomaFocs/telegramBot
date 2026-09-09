from telegram import Update, Chat
from telegram.ext import ContextTypes, ApplicationHandlerStop


async def ignora_canali(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	chat:Chat = update.effective_chat
	if chat is not None and chat.type == "channel":
		raise ApplicationHandlerStop
