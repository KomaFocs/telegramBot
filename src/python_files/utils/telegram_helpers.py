import asyncio
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from telegram import CallbackQuery, InlineKeyboardMarkup, Message, Update
from telegram.error import BadRequest, RetryAfter
from telegram.ext import ContextTypes

from src.python_files.models.image import Image
from src.python_files.utils.constants import (
	DEFAULT_STUN_DURATION,
	DIR,
	TAG_SEPARATOR,
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

	VALID_HOSTNAME:str = "furaffinity.net"
	raw_url:str = context.args[0].lower()

	if not raw_url.startswith(("http://", "https://")):
		raw_url = f"https://{raw_url}"

	parsed = urlparse(raw_url)

	if parsed.scheme != "https":
		parsed = parsed._replace(scheme="https")

	hostname: str = parsed.hostname or ""

	if hostname != VALID_HOSTNAME and not hostname.endswith(f".{VALID_HOSTNAME}"):
		return None

	return str(urlunparse(parsed))


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



def beautify_date(date:datetime|None, show_seconds:bool=False) -> str:
	date_string:str = (
		date.strftime("%d/%m/%Y %H:%M")
		if not show_seconds
		else date.strftime("%d/%m/%Y %H:%M:%S")
	)

	return (
		date_string
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


def get_spiegone() -> str:
	_LIMIT:int = 200
	_SPIEGONE:str = (
		"Telegram impedisce al bot di eliminare i messaggi più vecchi di 48 ore. Se desideri "
		"eliminare un tale messaggio, dovrai farlo manualmente."
	)
	return (
		_SPIEGONE
		if len(_SPIEGONE) <= _LIMIT
		else f"{_SPIEGONE[:_LIMIT-3].rsplit(' ', 1)[0]}..."
	)


def _clean_text(text: str, strict: bool) -> str:
	_MARKDOWN_TRANSLATE_TABLE= str.maketrans("", "", "*_~`>")
	if strict:
		return text.translate(_MARKDOWN_TRANSLATE_TABLE)
	return text


def rendi_grassetto(text:str, strict:bool=False) -> str:
	return f"*{_clean_text(text, strict)}*"

def rendi_corsivo(text:str, strict:bool=False) -> str:
	return f"_{_clean_text(text, strict)}_"

def rendi_sottolineato(text:str, strict:bool=False) -> str:
	return f"__{_clean_text(text, strict)}__"

def rendi_barrato(text:str, strict:bool=False) -> str:
	return f"~{_clean_text(text, strict)}~"

def	rendi_codice_inline(text:str, strict:bool=False) -> str:
	return f"`{_clean_text(text, strict)}`"

def rendi_citazione(text:str, strict:bool=False) -> str:
	return f">{_clean_text(text, strict)}"

def rendi_hyperlink(text:str, link:str, strict:bool=False) -> str:
	return f"[{_clean_text(text, strict)}]({link})"
