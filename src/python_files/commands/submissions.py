import asyncio
import logging
from traceback import print_exception

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from src.python_files.jobs.job_queue import JobQueue
from src.python_files.models.dao.image_dao import get_image, add_image
from src.python_files.models.dao.message_dao import (
	add_message, get_message, get_all_messages,
)
from src.python_files.models.dao.user_dao import add_user, get_user
from src.python_files.models.message import Message
from src.python_files.models.submission import Submission
from src.python_files.utils.constants import DIR, FA_URL, JOB_QUEUE, STATUS
from src.python_files.utils.decorators import logger, single_execution
from src.python_files.utils.fa_client import (
	find_next_button,
	get_all_submissions,
	send_request,
)
from src.python_files.utils.filters import filter_submissions, get_from_file


@logger
@single_execution()
async def submissions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

	user_id = str(update.effective_user.id)
	allowed_ids = get_from_file(DIR.SECRETS / "id.txt")

	if user_id not in allowed_ids:
		await update.message.reply_text(
			"Spiacente, non sei autorizzato a usare questo comando :S"
		)
		return

	status_message = await update.message.reply_text(
		"Richiesta ricevuta..."
	)

	try:
		messages = get_all_messages([STATUS.PENDING, STATUS.APPROVED])

		if messages:
			await status_message.edit_text(
				"Ci sono submission presenti nel database: "
				"non effettuo una nuova ricerca su internet."
			)

			job_queue: JobQueue = context.application.bot_data[JOB_QUEUE]
			job_queue.notify()
			return

		current_url = f"{FA_URL}/msg/submissions"
		visited_urls: set[str] = set()
		all_submissions: list[Submission] = []

		await context.bot.send_chat_action(
			chat_id=update.effective_chat.id,
			action=ChatAction.TYPING,
		)

		while current_url and current_url not in visited_urls:
			visited_urls.add(current_url)

			response = await send_request(url=current_url)
			current_url = find_next_button(response)

			all_submissions.extend(
				get_all_submissions(response)
			)

		filtered_submissions: list[Submission] = filter_submissions(
			all_submissions
		)

		await asyncio.sleep(2)

		added = 0
		skipped = 0

		for filtered in filtered_submissions:
			image = get_image(filtered.image.image_id)

			if image is None:
				user = get_user(filtered.user.username)

				if user is None:
					add_user(filtered.user)

				add_image(filtered.image)

			message = get_message(filtered.image.image_id)

			if message is not None:
				skipped += 1
				continue

			message = Message(
				image_id=filtered.image.image_id,
				username=filtered.user.username,
				status=STATUS.PENDING,
			)

			add_message(message)
			added += 1

		job_queue: JobQueue = context.application.bot_data[JOB_QUEUE]
		job_queue.notify()

		await status_message.edit_text(
			f"Ricerca completata.\n"
			f"Nuove submission: {added}\n"
			f"Già presenti: {skipped}"
		)

	except Exception as e:
		error_msg = "Errore durante il recupero delle submission"
		logging.error(error_msg, exc_info=e)
		await status_message.edit_text(error_msg)