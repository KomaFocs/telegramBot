from telegram import Update
from telegram.constants import ChatType
from telegram.ext import ContextTypes, ApplicationHandlerStop


async def ignora_canali(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	chat = update.effective_chat or (update.channel_post.chat if update.channel_post else None)
	if chat is None:
		return

	if chat.type == ChatType.CHANNEL:
		# time_log(f"[({update.effective_chat.id})-({update.effective_chat.title})]")
		raise ApplicationHandlerStop
