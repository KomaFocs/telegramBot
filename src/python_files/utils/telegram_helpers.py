import asyncio
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.constants import ChatType
from telegram.error import BadRequest, RetryAfter
from telegram.ext import ContextTypes

from src.python_files.models.image import Image
from src.python_files.models.submission import Submission
from src.python_files.utils.constants import (
	CALLBACKS,
	DEFAULT_STUN_DURATION,
	DIR,
	MAX_TAGS_IN_MESSAGE,
	TAG_SEPARATOR, STATUS,
)


def _load_tags(path: Path) -> set[str]:
	if not path.exists():
		return set()
	return {
		line.strip().lower()
		for line in path.read_text(encoding="utf-8").splitlines()
		if line.strip()
	}


def check_url(context: ContextTypes.DEFAULT_TYPE) -> str | None:
	if not context.args:
		return None

	VALID_HOSTNAME = "furaffinity.net"
	raw_url = context.args[0]

	url_to_parse = raw_url if raw_url.lower().startswith(("http://", "https://")) else f"https://{raw_url}"

	parsed = urlparse(url_to_parse)
	hostname = parsed.hostname.lower() if parsed.hostname else ""

	if hostname != VALID_HOSTNAME and not hostname.endswith(f".{VALID_HOSTNAME}"):
		return None

	return parsed._replace(scheme="https").geturl()


async def delete_messages(message_list: list[Message], delay: int | None = None) -> None:
	if delay and delay > 0:
		await asyncio.sleep(delay)

	for message in message_list:
		try:
			await message.delete()
			await asyncio.sleep(0.1)  # per evitare Flood Control
		except Exception as e:
			print(f"{e}: Failed to delete message '{message}'.")


async def resume_operations(update: Update, context: ContextTypes.DEFAULT_TYPE, messages: list[Message], delay: int = DEFAULT_STUN_DURATION) -> None:
	await delete_messages(message_list=messages, delay=delay)
	msg: str = "Non ho informazioni su /guida guida e tu non hai mai richiesto una cosa simile, haha immagina farlo haha"
	await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def get_chat_id_from_file(file: str | Path) -> int | None:
	path = Path(file)
	if not path.exists():
		return None
	return int(path.read_text(encoding="utf-8").strip())


def format_text(submission: Submission, chat: ChatType) -> str:
	text: str = f"{submission.image.title}\n\n"

	match chat:
		case ChatType.GROUP:
			text += beautify_date(submission.message.scheduled_at)
		case ChatType.CHANNEL:
			text += TAG_SEPARATOR.join(get_filtered_tags(submission.image)[:MAX_TAGS_IN_MESSAGE])
		case _:
			text = "WTF"

	return text


def beautify_date(date: datetime | None) -> str:
	return (
		date.strftime("%d/%m/%Y %H:%M")
		if date
		else "Non programmato"
	)


def _clean_tag(tag: str) -> str:
	if len(tag) >= 2 and tag[0].isalpha() and tag[1] == "_":
		return ""

	return f"#{tag.replace('-', '_')}"


_PRIORITY_TAGS = _load_tags(DIR.PRIORITY_TAGS_FILE)
_SPECIES = _load_tags(DIR.SPECIES_FILE)


def _is_species_tag(tag: str) -> bool:
	tag = re.sub(r"[_-]", "", tag.lower())
	return any(
		re.search(species, tag)
		for species in _SPECIES
	)


def get_filtered_tags(image: Image) -> list[str]:
	priority_tags: list[str] = []
	other_tags: list[str] = []

	for tag in image.tags.split(sep=TAG_SEPARATOR):
		t = _clean_tag(tag)

		if not t or _is_species_tag(t):
			continue

		if t.lstrip("#").lower() in _PRIORITY_TAGS:
			priority_tags.append(t)
		else:
			other_tags.append(t)

	return priority_tags + other_tags


async def safe_edit_markup(query: CallbackQuery, reply_markup: InlineKeyboardMarkup | None) -> None:
	try:
		await query.edit_message_reply_markup(reply_markup=reply_markup)
	except RetryAfter as e:
		await asyncio.sleep(e.retry_after)
		await query.edit_message_reply_markup(reply_markup=reply_markup)
	except BadRequest:
		pass



def get_channel_keyboard(submission:Submission) -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(
				text=f"{submission.user.display_name}",
				url=f"{submission.user.link}"
			),
			InlineKeyboardButton(
				text=f"🔗 Apri il link",
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



def _clean_text(text: str, strict: bool) -> str:
	_MARKDOWN_TRANSLATE_TABLE= str.maketrans("", "", "*_~`>")
	if strict:
		return text.translate(_MARKDOWN_TRANSLATE_TABLE)
	return text

def grassetto(text:str, strict:bool=False) -> str:
	return f"*{_clean_text(text, strict)}*"

def corsivo(text:str, strict:bool=False) -> str:
	return f"_{_clean_text(text, strict)}_"

def sottolineato(text:str, strict:bool=False) -> str:
	return f"__{_clean_text(text, strict)}__"

def barrato(text:str, strict:bool=False) -> str:
	return f"~{_clean_text(text, strict)}~"

def	codice_inline(text:str, strict:bool=False) -> str:
	return f"`{_clean_text(text, strict)}`"

def citazione(text:str, strict:bool=False) -> str:
	return f">{_clean_text(text, strict)}"

def hyperlink(text:str, link:str, strict:bool=False) -> str:
	return f"[{_clean_text(text, strict)}]({link})"
