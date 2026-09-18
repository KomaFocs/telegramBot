import asyncio
from asyncio import Task
from collections.abc import Callable

from telegram import (
	Update,
	CallbackQuery, InlineKeyboardMarkup, Message,
)
from telegram.ext import ContextTypes

from src.python_files.models.dao.message_dao import update_message, get_message
from src.python_files.utils.constants import STATUS
from src.python_files.utils.telegram_helpers import safe_edit_markup, do_reject_keyboard, \
	confirm_reject_keyboard, confirm_change_your_mind_keyboard, do_change_your_mind_keyboard

pending_confirmations = {}


async def countdown_task(
		query:CallbackQuery, image_id:int,
		countdown_keyboard_fn:Callable[[int,int], InlineKeyboardMarkup],
		timeout_keyboard_fn:Callable[[int], InlineKeyboardMarkup],
		total: int = 30, step: int = 5) -> None:

	step = 5 if step < 5 or step > 30 else step
	total = 30 if total < 0 or total > 60 else total

	try:
		for seconds_left in range(total, 0, -step):
			await safe_edit_markup(query, countdown_keyboard_fn(image_id, seconds_left))
			await asyncio.sleep(step)

		await safe_edit_markup(query, timeout_keyboard_fn(image_id))

	except asyncio.CancelledError:
		pass
	finally:
		pending_confirmations.pop(image_id, None)


async def handle_callback(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	query:CallbackQuery = update.callback_query
	data = query.data
	image_id:int = int(data.split(":")[1])
	if not isinstance(query.message, Message):
		await query.answer("Errore: messaggio non più accessibile.", show_alert=True)
		return
	current_caption:str = query.message.caption or ""
	base_caption:str = current_caption.split("\n\n❌")[0].split("\n\n✅")[0].strip()

	if image_id in pending_confirmations:
		pending_confirmations[image_id].cancel()

	if data.startswith("confirm_reject"):
		task:Task = asyncio.create_task(
			countdown_task(
				query=query,
				image_id=image_id,
				countdown_keyboard_fn=do_reject_keyboard,
				timeout_keyboard_fn=confirm_reject_keyboard,
			)
		)
		pending_confirmations[image_id] = task
		await query.answer("Annullamento programmazione messaggio...")

	elif data.startswith("do_reject"):
		message = get_message(image_id)
		if message:
			message.status = STATUS.REJECTED
			update_message(message)

			new_caption = (
				f"{base_caption}\n\n"
				"❌ Messaggio tolto dalla coda!\n"
				"Se cambi idea, clicca il tasto qui sotto per approvare il messaggio."
			)
			await query.edit_message_caption(
				caption=new_caption,
				reply_markup=confirm_change_your_mind_keyboard(image_id=image_id)
			)
			await query.answer("Programmazione del messaggio annullata.")

	elif data.startswith("nevermind"):
		task:Task = asyncio.create_task(
			countdown_task(
				query=query,
				image_id=image_id,
				countdown_keyboard_fn=do_change_your_mind_keyboard,
				timeout_keyboard_fn=confirm_change_your_mind_keyboard,
			)
		)
		pending_confirmations[image_id] = task
		await query.answer("Cambio idea in corso...")

	elif data.startswith("do_approve"):
		message = get_message(image_id)
		if message:
			message.status = STATUS.APPROVED
			update_message(message)

			new_caption = f"{base_caption}\n\n✅ Messaggio approvato!"
			await query.edit_message_caption(
				caption=new_caption,
				reply_markup=confirm_reject_keyboard(image_id=image_id)
			)
			await query.answer("Messaggio approvato.")
