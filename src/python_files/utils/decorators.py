import datetime
from functools import wraps
from typing import Callable, Any
from telegram import Update, User
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

_processing_users:set[int] = set()
def single_execution(fallback_message:str = "⏳ Aspetta prima di inviare un altro comando!"):
	"""Assicura che la funzione termini prima di essere eseguita nuovamente"""
	def decorator(func:Callable[..., Any]):
		@wraps(func)
		async def wrapper(update:Update, context:ContextTypes, *args, **kwargs):
			user:User = update.effective_user
			if not user:
				return await func(update, context, *args, **kwargs)
			user_id:int = user.id
			if user_id in _processing_users:
				if update.callback_query:
					await update.callback_query.answer(fallback_message, show_alert=True)
				elif update.message:
					await update.message.reply_text(fallback_message)
				return None

			_processing_users.add(user_id)

			try:
				return await func(update, context, *args, **kwargs)
			finally:
				_processing_users.discard(user_id)
		return wrapper
	return decorator



def logger(function):
	@wraps(function)
	def wrapper(*args, **kwargs):
		cmd:str = function.__name__.split("_")[0]
		update:Update = args[0]
		first_name:str = update.message.from_user.first_name
		now = datetime.datetime.now()
		data = now.strftime("%d/%m/%Y")
		orario = now.strftime("%H:%M:%S")
		print(f"[{data} {orario}] {first_name} used the {cmd} command.")
		return function(*args, **kwargs)
	return wrapper


def chat_action(action:ChatAction = ChatAction.TYPING):
	"""Fa sì che venga inviato in chat una ChatAction, di default ChatAction.TYPING"""
	# FIXME if chataction != bello
	def decorator(func:Callable[..., Any]):
		@wraps(func)
		async def wrapper(update:Update, context:ContextTypes, *args, **kwargs):
			if update and update.effective_chat:
				await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=action)
			return await func(update, context, *args, **kwargs)
		return wrapper
	return decorator
