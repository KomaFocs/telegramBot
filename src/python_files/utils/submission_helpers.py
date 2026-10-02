from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatType
from telegram.helpers import escape_markdown

from src.python_files.models.submission import Submission
from src.python_files.utils.constants import (
	MAX_TAGS_IN_MESSAGE,
	TAG_SEPARATOR, CALLBACKS, STATUS, SPIEGONE_ELIMINAZIONE,
)
from src.python_files.utils.cooldown import stun_bot
from src.python_files.utils.telegram_helpers import beautify_date, get_filtered_tags, rendi_hyperlink, rendi_grassetto


def format_text(submission: Submission, chat: ChatType) -> str:
	to_fix = [submission.name_user, submission.image.title, beautify_date(submission.scheduled_at)]
	name_user, title, scheduled_at = [escape_markdown(str(s), version=2) for s in to_fix]

	text:str = (
		f"{rendi_grassetto(name_user)} \- {rendi_hyperlink(
			text=title,
			link=submission.image.submission_link,
			strict=False,
		)}\n\n"
	)

	match chat:
		case ChatType.GROUP:
			text += f"Previsto per: {scheduled_at}"
		case ChatType.CHANNEL:
			tags:list[str] = get_filtered_tags(submission.image)[:MAX_TAGS_IN_MESSAGE]
			escaped_tags:list[str] = [escape_markdown(str(tag), version=2) for tag in tags]
			text += TAG_SEPARATOR.join(escaped_tags)
		case _:
			text += ""

	return text


def get_channel_keyboard(submission:Submission) -> InlineKeyboardMarkup|None:
	# Telegram impedisce agli utenti di aggiungere commenti al messaggio se è presente una tastiera
	return None

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


def get_expired_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(
				text="Eliminare manualmente (>48h)",
				callback_data=f"{SPIEGONE_ELIMINAZIONE}:{CALLBACKS.NONE}"
			)
		]
	])


def get_poll_keyboard(chat_type:ChatType) -> InlineKeyboardMarkup|None:
	if chat_type == ChatType.CHANNEL: return None

	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(
				text="📤Invia al canale",
				callback_data=f"{CALLBACKS.PUBLISH_POLL}:{CALLBACKS.PUBLISH_POLL}"
			)
		]
	])