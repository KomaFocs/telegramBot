import asyncio
from asyncio import Task
from collections.abc import Callable

from telegram import CallbackQuery, InlineKeyboardMarkup, Message as TelegramMessage, Update
from telegram.ext import ContextTypes

from src.python_files.models.dao.submission_dao import SubmissionDAO
from src.python_files.models.submission import Submission
from src.python_files.utils.constants import CALLBACKS, JOB_QUEUE, STATUS
from src.python_files.utils.telegram_helpers import (
	safe_edit_markup, get_countdown_keyboard, get_group_keyboard,
)

pending_confirmations: dict[int, Task] = {}


async def countdown_task(
	query: CallbackQuery,
	submission: Submission,
	countdown_keyboard_fn: Callable[[Submission, int], InlineKeyboardMarkup],
	timeout_keyboard_fn: Callable[[Submission], InlineKeyboardMarkup],
	total: int = 30,
	step: int = 5,
) -> None:
	image_id = submission.image.image_id
	current_task = asyncio.current_task()

	step = 5 if step < 5 or step > 30 else step
	total = 30 if total < 0 or total > 60 else total

	try:
		for seconds_left in range(total, 0, -step):
			await safe_edit_markup(
				query,
				countdown_keyboard_fn(submission, seconds_left)
			)
			await asyncio.sleep(step)

		await safe_edit_markup(
			query,
			timeout_keyboard_fn(submission),
		)

	except asyncio.CancelledError:
		pass

	finally:
		if pending_confirmations.get(image_id) is current_task:
			# Pycharm crede che .pop() sia una coroutine senza la variabile '_'
			_ = pending_confirmations.pop(image_id, None)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	query:CallbackQuery = update.callback_query

	if not isinstance(query.message, TelegramMessage):
		await query.answer(text="Errore: messaggio non più accessibile.", show_alert=True)
		return

	data = query.data or ""
	split_data = data.lower().split(":", 1)

	if len(split_data) < 2 or split_data[0] == CALLBACKS.NONE or split_data[1] == CALLBACKS.NONE:
		text = ""
		if query.message.reply_markup:
			for row in query.message.reply_markup.inline_keyboard:
				for button in row:
					if button.callback_data == query.data:
						text = button.text
						break

		await query.answer(text)
		return

	try:
		image_id = int(split_data[1])
	except ValueError:
		await query.answer(text=f"Identificativo immagine {split_data[1] if split_data[1] else ""} non valido.", show_alert=True)
		return

	submission:Submission = SubmissionDAO.get_submission_by_id(image_id)

	if submission is None:
		await query.answer(text="Submission non trovata.", show_alert=True)
		return

	current_caption = query.message.caption or ""
	base_caption = (
		current_caption
		.split("\n\n❌")[0]
		.split("\n\n✅")[0]
		.strip()
	)

	existing_task = pending_confirmations.pop(image_id, None)
	if existing_task is not None:
		existing_task.cancel()

	job_queue = context.bot_data.get(JOB_QUEUE)
	action: str = split_data[0]

	match action:
		case CALLBACKS.PROMPT_REJECT | CALLBACKS.PROMPT_APPROVE:
			task: Task = asyncio.create_task(
				countdown_task(
					query=query,
					submission=submission,
					countdown_keyboard_fn=get_countdown_keyboard,
					timeout_keyboard_fn=get_group_keyboard,
				)
			)
			pending_confirmations[image_id] = task
			await query.answer()

		case CALLBACKS.DO_REJECT:
			submission.message.status = STATUS.REJECTED
			submission.scheduled_at = None

			SubmissionDAO.update_submission(submission=submission)

			if job_queue:
				job_queue.notify()

			new_caption = (
				f"{base_caption}\n\n"
				"❌ Messaggio tolto dalla coda!\n"
				"Se cambi idea, clicca il tasto qui sotto per approvare il messaggio."
			)

			await query.edit_message_caption(
				caption=new_caption,
				reply_markup=get_group_keyboard(submission=submission)
			)
			await query.answer(f"Messaggio {submission.image_id} di {submission.user} rifiutato.")

		case CALLBACKS.DO_APPROVE:
			submission.message.status = STATUS.APPROVED

			SubmissionDAO.update_submission(submission)

			if job_queue:
				job_queue.notify()

			new_caption = (
				f"{base_caption}\n\n"
				"✅ Messaggio approvato! Se cambi idea e vuoi annullare, clicca il tasto qui sotto."
			)

			await query.edit_message_caption(
				caption=new_caption,
				reply_markup=get_group_keyboard(submission=submission)
			)
			await query.answer(f"Messaggio {submission.image_id} di {submission.user} approvato.")

		case CALLBACKS.NONE:
			await query.answer()