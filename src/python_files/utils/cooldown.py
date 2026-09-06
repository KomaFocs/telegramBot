import time
from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop
from src.python_files.utils.constants import DEFAULT_STUN_DURATION, STUNNED_STRING, DELETE_INCOMING_MESSAGES


def stun_bot(context:ContextTypes.DEFAULT_TYPE, user_id:int=-1, duration:int=DEFAULT_STUN_DURATION) -> None:
	context.user_data[STUNNED_STRING] = time.time() + duration


def is_bot_stunned(context:ContextTypes.DEFAULT_TYPE, user_id:int=-1) -> tuple[bool, int]:
	stunned_until = context.user_data.get(STUNNED_STRING, 0)

	now = time.time()
	if now < stunned_until:
		return True, int(stunned_until - now)

	return False, 0


async def stunned(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	bot_stunned = is_bot_stunned(context)[0]
	deleting = context.user_data.get(DELETE_INCOMING_MESSAGES, False)

	if not bot_stunned and not deleting:
		return

	if deleting:
		message = update.effective_message
		if message and message.from_user and not message.from_user.is_bot:
			try:
				await message.delete()
			except Exception as e:
				print(e)


	raise ApplicationHandlerStop
