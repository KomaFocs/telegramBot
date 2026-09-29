from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatType

from src.python_files.models.submission import Submission
from src.python_files.utils.constants import (
	MAX_TAGS_IN_MESSAGE,
	TAG_SEPARATOR, CALLBACKS, STATUS,
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

def get_channel_keyboard(submission:Submission) -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(
				text=f"{submission.user.display_name}",
				url=f"{submission.user.link}"
			),
			InlineKeyboardButton(
				text=f"🔗 Apri link",
				url=f"{submission.image.submission_link}"
			)
		]
	])


def get_group_keyboard(submission:Submission) -> InlineKeyboardMarkup:
	button_text:str = ""
	callback_action:str = ""

	match submission.status:
		case STATUS.PENDING | STATUS.APPROVED:
			button_text = "❌ Rifiuta"
			callback_action = f"{CALLBACKS.PROMPT_REJECT}:{submission.image_id}"

		case STATUS.REJECTED:
			button_text = "✅ Approva"
			callback_action = f"{CALLBACKS.PROMPT_APPROVE}:{submission.image_id}"

		case _:
			pass

	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(
				text=f"Stato: {submission.status_text}",
				callback_data=f"{CALLBACKS.NONE}:{CALLBACKS.NONE}"
			),
			InlineKeyboardButton(
				text=button_text,
				callback_data=callback_action
			)
		]
	])


def get_countdown_keyboard(submission: Submission, seconds: int) -> InlineKeyboardMarkup:
	"""Tastiera di conferma durante il countdown."""
	text:str = ""
	callback:str = ""

	match submission.status:
		case STATUS.REJECTED:
			text = f"✅ Confermi? {seconds}s ⏰"
			callback = f"{CALLBACKS.DO_APPROVE}:{submission.image_id}"

		case STATUS.PENDING | STATUS.APPROVED:
			text = f"❌ Confermi? {seconds}s ⏰"
			callback = f"{CALLBACKS.DO_REJECT}:{submission.image_id}"

		case _:
			text = callback = f"{CALLBACKS.NONE}:{CALLBACKS.NONE}"


	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(
				text=text,
				callback_data=f"{callback}"
			)
		]
	])


def get_submission_keyboard(submission:Submission, chat_type:ChatType) -> InlineKeyboardMarkup|None:
	match chat_type:
		case ChatType.GROUP:
			return get_group_keyboard(submission)

		case ChatType.CHANNEL:
			return get_channel_keyboard(submission)

		case _:
			return None

