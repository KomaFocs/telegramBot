import traceback
from functools import wraps
from traceback import StackSummary, FrameSummary
from datetime import datetime
from typing import Callable, Any

from sqlalchemy.exc import IntegrityError
from telegram import Update, User
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from src.python_files.config.database import get_session
from src.python_files.utils.telegram_helpers import beautify_date

_processing_users:set[int] = set()
def single_execution(fallback_message:str = "⏳ Aspetta prima di inviare un altro comando!", verbose:bool = True):
	"""Assicura che la funzione termini prima di essere eseguita nuovamente"""
	def decorator(func:Callable[..., Any]):
		@wraps(func)
		async def wrapper(update:Update, context:ContextTypes, *args, **kwargs):
			user:User = update.effective_user
			if not user:
				return await func(update, context, *args, **kwargs)
			user_id:int = user.id
			if user_id in _processing_users:
				if verbose:
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
		now = datetime.now()
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


def integrity_error(func:Callable[..., Any]) -> Callable[..., Any]:
	"""Ignora silenziosamente IntegrityError facendo rollback"""
	@wraps(func)
	def wrapper(*args, **kwargs):
		with get_session() as session:
			try:
				return func(*args, **kwargs)
			except IntegrityError:
				session.rollback()
				return None

	return wrapper


def error_origin(local_only: bool = False):
	"""local_only = True => cerca la causa dell'errore soltanto nei file utente anziché nelle librerie"""

	def decorator(func):
		@wraps(func)
		async def wrapper(*args, **kwargs):
			try:
				return await func(*args, **kwargs)
			except Exception as exc:
				if exc.__traceback__:
					tb_list: traceback.StackSummary = traceback.extract_tb(exc.__traceback__)

					if local_only:
						# Cerca il primo frame nei file di progetto (escludendo site-packages)
						frame: traceback.FrameSummary = next(
							(f for f in reversed(tb_list) if "site-packages" not in f.filename),
							tb_list[-1]
						)
					else:
						frame: traceback.FrameSummary = tb_list[-1]


					relative_path = f"src{frame.filename.split("src")[1]}"
					print(
						f"[{beautify_date(datetime.now())}] "
						f"Errore originato da: '{frame.name}()'\n"
						f"Funzione in: {frame.filename}\n"
						f"Riga {frame.lineno}\n"
						f"Eccezione: {type(exc).__name__}: {exc}\n\n"
					)
				raise exc
		return wrapper
	return decorator