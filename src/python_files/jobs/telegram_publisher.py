import time
from datetime import datetime

from telegram import Message
from telegram.ext import Application, ExtBot

from src.python_files.models.submission import Submission
from src.python_files.utils.constants import DIR
from src.python_files.utils.telegram_helpers import get_chat_id_from_file


class TelegramPublisher:
	GROUP_ID:int = get_chat_id_from_file(DIR.GROUP_TEST)
	CHANNEL_ID:int = get_chat_id_from_file(DIR.CHANNEL_TEST)

	def __init__(self, application: Application) -> None:
		self._bot: ExtBot = application.bot

	async def send_to_group(self, submission:Submission) -> Message:
		image = submission.image

		text = (
			f"{image.submission_link} - "
			f"{image.title} - "
			f"{self.beautify_date(submission.message.scheduled_at)}"
		)

		message: Message = await self._bot.send_message(
			chat_id=self.GROUP_ID,
			text=text,
		)

		print(
			f"Messaggio inviato {message.message_id} "
			f"al gruppo {message.chat.title}"
		)
		return message

	async def send_to_channel(self, submission:Submission) -> Message:
		image = submission.image

		text = (
			f"{image.submission_link} - "
			f"{image.title}"
		)

		message:Message = await self._bot.send_message(
			chat_id=self.CHANNEL_ID,
			text=text,
		)

		print(
			f"Messaggio inviato {message.message_id} "
			f"al canale {message.chat.title}"
		)

		return message

	@staticmethod
	def beautify_date(date:datetime | None) -> str:
		if date is None:
			return "Non programmato"

		return date.strftime("%d/%m/%Y %H:%M")


	async def send_to_group_2(self, submission: Submission) -> Message:
		image = submission.image

		text = (
			f"{image.submission_link} - "
			f"{image.title} - "
			f"{self.beautify_date(submission.message.scheduled_at)}"
		)

		print(f"INVIO: {image.image_id}")
		start = time.monotonic()

		try:
			message: Message = await self._bot.send_message(
				chat_id=self.GROUP_ID,
				text=text,
			)
		except Exception:
			print(
				f"ERRORE dopo {time.monotonic() - start:.2f}s: "
				f"{image.image_id}"
			)
			raise

		print(
			f"OK dopo {time.monotonic() - start:.2f}s: "
			f"{image.image_id}"
		)

		return message