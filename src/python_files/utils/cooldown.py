import time
from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop
from src.python_files.utils.constants import DEFAULT_STUN_DURATION, HIOSHIRU, DIR, STUNNED_STRING


def stun_bot(context:ContextTypes.DEFAULT_TYPE, user_id:int=-1, duration:int=DEFAULT_STUN_DURATION) -> None:
	context.user_data[STUNNED_STRING] = time.time() + duration


def is_bot_stunned(context:ContextTypes.DEFAULT_TYPE, user_id:int=-1) -> tuple[bool, int]:
	stunned_until = context.user_data.get(STUNNED_STRING, 0)

	now = time.time()
	if now < stunned_until:
		return True, int(stunned_until - now)

	return False, 0


async def stunned(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	bot_stunned, _ = is_bot_stunned(context)

	if bot_stunned:
		with open(DIR.SECRETS/HIOSHIRU, "r") as file:
			sticker = file.read().split()[3]
		await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=sticker)
		raise ApplicationHandlerStop