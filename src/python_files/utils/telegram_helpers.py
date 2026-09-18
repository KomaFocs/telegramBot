import asyncio
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from telegram import Message, Update, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.constants import ChatType
from telegram.error import RetryAfter, BadRequest
from telegram.ext import ContextTypes

from src.python_files.models.image import Image
from src.python_files.models.submission import Submission
from src.python_files.utils.constants import DEFAULT_STUN_DURATION, DIR, TAG_SEPARATOR, MAX_TAGS_IN_MESSAGE


def _load_tags(path:Path) -> set[str]:
	with open(path) as f:
		return {
			line.strip().lower()
			for line in f
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


async def resume_operations(update:Update, context:ContextTypes.DEFAULT_TYPE, messages:list[Message], delay:int=DEFAULT_STUN_DURATION):
	await delete_messages(message_list=messages, delay=delay)
	msg:str = "Non ho informazioni su /guida guida e tu non hai mai richiesto una cosa simile, haha immagina farlo haha"
	await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def get_chat_id_from_file(file:str | Path) -> int | None:
	with open(file, "r") as f:
		return int(f.read().strip())


def format_text(submission:Submission, chat:ChatType) -> str:
	text:str = f"{submission.image.title}\n\n"

	match chat:
		case ChatType.GROUP:
			text += beautify_date(submission.message.scheduled_at)
		case ChatType.CHANNEL:
			text += TAG_SEPARATOR.join(get_filtered_tags(submission.image)[:MAX_TAGS_IN_MESSAGE])
		case _: text = "WTF"

	return text


def beautify_date(date:datetime|None) -> str:
	return (
		date.strftime("%d/%m/%Y %H:%M")
		if date
		else "Non programmato"
	)


def _clean_tag(tag:str) -> str:
	if len(tag) >= 2 and tag[0].isalpha() and tag[1] == "_":
		return ""

	return f"#{tag.replace('-', '_')}"


_PRIORITY_TAGS = _load_tags(DIR.PRIORITY_TAGS_FILE)
_SPECIES = _load_tags(DIR.SPECIES_FILE)


def _is_species_tag(tag:str) -> bool:
	tag = re.sub(r"[_-]", "", tag.lower())
	return any(
		re.search(species, tag)
		for species in _SPECIES
	)


def get_filtered_tags(image:Image) -> list[str]:
	priority_tags:list[str] = []
	other_tags:list[str] = []

	for tag in image.tags.split(sep=TAG_SEPARATOR):
		t = _clean_tag(tag)

		if not t or _is_species_tag(t):
			continue

		if t.lstrip("#").lower() in _PRIORITY_TAGS:
			priority_tags.append(t)
		else:
			other_tags.append(t)

	return priority_tags + other_tags


async def safe_edit_markup(query:CallbackQuery, reply_markup) -> None:
	try:
		await query.edit_message_reply_markup(reply_markup=reply_markup)
	except RetryAfter as e:
		await asyncio.sleep(e.retry_after)
		await query.edit_message_reply_markup(reply_markup=reply_markup)
	except BadRequest:
		pass


def confirm_reject_keyboard(image_id:int) -> InlineKeyboardMarkup:
	"""❌ Annulla invio"""
	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(
				text="❌ Annulla invio", callback_data=f"confirm_reject:{image_id}"
			)
		]
	])


def do_reject_keyboard(image_id:int, seconds:int) -> InlineKeyboardMarkup:
	"""⏰ Annulla invio: premi di nuovo per confermare"""
	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(
				text=f"⏰ Annulla invio: premi di nuovo per confermare ({seconds}s)", callback_data=f"do_reject:{image_id}"
			)
		]
	])


def confirm_change_your_mind_keyboard(image_id:int) -> InlineKeyboardMarkup:
	"""🤔 Clicca qui per cambiare idea"""
	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(
				text="🤔 Clicca qui per cambiare idea",callback_data=f"nevermind:{image_id}"
			)
		]
	])

def do_change_your_mind_keyboard(image_id:int, seconds:int) -> InlineKeyboardMarkup:
	"""⚠️ Confermi di voler approvare questo messaggio?"""
	return InlineKeyboardMarkup([
		[
			InlineKeyboardButton(
				text=f"⚠️ Confermi di voler approvare questo messaggio? ({seconds}s)",callback_data=f"do_approve:{image_id}"
			)
		]
	])