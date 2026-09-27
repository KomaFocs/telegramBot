import logging

from telegram import Update, Message as TelegramMessage
from telegram.ext import ContextTypes

from src.python_files.jobs.post_init import check_pending_messages
from src.python_files.models.dao.submission_dao import SubmissionDAO
from src.python_files.models.submission import Submission
from src.python_files.utils.constants import DIR
from src.python_files.utils.decorators import logger, single_execution
from src.python_files.utils.filters import get_from_file
from src.python_files.utils.telegram_helpers import beautify_date


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

	status_message:TelegramMessage = await update.message.reply_text("Ci sto lavorando...")

	try:
		await check_pending_messages()
		submissions:list[Submission] = SubmissionDAO.get_submissions(scheduled=True)

		if not submissions:
			await status_message.edit_text("Nessuna submission programmata trovata.")
			return

		text:str = "\n\n".join([
			f"{submission.image.title} - {submission.name_user} ({submission.image_id})\n{beautify_date(submission.scheduled_at)}"
			for submission in submissions
		])
		text = f"Ho trovato le seguenti immagini da pubblicare:\n{text}"

		await status_message.edit_text(text=text, parse_mode="Markdown")

	except Exception as e:
		error_msg = "Errore durante il recupero delle submission"
		logging.error(error_msg, exc_info=e)
		await status_message.edit_text(error_msg)