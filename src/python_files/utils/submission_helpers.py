from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatType

from src.python_files.models.submission import Submission
from src.python_files.utils.constants import (
	MAX_TAGS_IN_MESSAGE,
	TAG_SEPARATOR,
)
from src.python_files.utils.telegram_helpers import beautify_date, get_filtered_tags


def format_text(submission: Submission, chat: ChatType) -> str:
	text = f"{submission.image.title}\n\n"

	match chat:
		case ChatType.GROUP:
			text += beautify_date(submission.message.scheduled_at)

		case ChatType.CHANNEL:
			text += TAG_SEPARATOR.join(
				get_filtered_tags(submission.image)[:MAX_TAGS_IN_MESSAGE]
			)

		case _:
			text = "WTF"

	return text


def confirm_reject_keyboard(
	submission: Submission,
) -> InlineKeyboardMarkup:
	image_id = submission.image.image_id
	status = submission.message.status

	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(
				text=f"Status: {status}",
				callback_data=f"none:none",
			),
			InlineKeyboardButton(
				text="❌ Annulla invio",
				callback_data=f"confirm_reject:{image_id}",
			),
		]
	])


def do_reject_keyboard(submission: Submission, seconds: int) -> InlineKeyboardMarkup:
	image_id = submission.image.image_id

	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(
				text=f"⏰ Confermi di voler annullare? ({seconds}s)",
				callback_data=f"do_reject:{image_id}",
			),
		]
	])


def confirm_change_your_mind_keyboard(submission: Submission) -> InlineKeyboardMarkup:
	image_id = submission.image.image_id
	status = submission.message.status

	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(
				text=f"Status: {status}",
				callback_data="none:none",
			),
			InlineKeyboardButton(
				text="🤔 Clicca qui per cambiare idea",
				callback_data=f"nevermind:{image_id}",
			),
		]
	])


def do_change_your_mind_keyboard(submission:Submission, seconds:int) -> InlineKeyboardMarkup:
	image_id = submission.image.image_id

	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(
				text=f"⚠️ Confermi di voler approvare? ({seconds}s)",
				callback_data=f"do_approve:{image_id}",
			),
		]
	])
