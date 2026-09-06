import asyncio
from urllib.parse import urlparse, ParseResult

from telegram import Message, Update
from telegram.ext import ContextTypes

from src.python_files.utils.constants import DEFAULT_STUN_DURATION


def check_url(context: ContextTypes.DEFAULT_TYPE) -> str | None:
	if not context.args: return None

	VALID_HOSTNAME = "furaffinity.net"
	raw_url:str = next((arg for arg in context.args if VALID_HOSTNAME in arg.lower()), None)
	if not raw_url: return None

	url_to_parse:str = raw_url if raw_url.lower().startswith("http://", "https://") else f"https://{raw_url}"
	parsed:ParseResult = urlparse(url_to_parse)
	hostname:str = parsed.hostname.lower() if parsed.hostname else ""
	if hostname == VALID_HOSTNAME or hostname.endswith(VALID_HOSTNAME):
		return parsed._replace(scheme="https").geturl()

	return None



async def delete_messages(message_list: list[Message], delay: int | None = None) -> None:
	if delay and delay > 0:
		await asyncio.sleep(delay)

	for message in message_list:
		try:
			await message.delete()
			await asyncio.sleep(0.1)  # Micro-pausa per evitare Flood Control
		except Exception:
			pass


async def resume_operations(update:Update, context:ContextTypes.DEFAULT_TYPE, messages:list[Message], delay:int=DEFAULT_STUN_DURATION):
	await delete_messages(message_list=messages, delay=delay)
	msg:str="Non ho informazioni su /guida guida e tu non hai mai richiesto una cosa simile, haha immagina farlo haha"
	await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
