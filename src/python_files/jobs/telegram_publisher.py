from telegram import Message as TelegramMessage, InlineKeyboardMarkup
from telegram.constants import ChatType, ParseMode
from telegram.ext import Application, ExtBot

from src.python_files.models.dao.submission_dao import SubmissionDAO
from src.python_files.models.image import Image
from src.python_files.models.submission import Submission
from src.python_files.utils.constants import DIR, STATUS
from src.python_files.utils.decorators import error_origin
from src.python_files.utils.fa_client import prepare_img_to_send
from src.python_files.utils.telegram_helpers import get_chat_id_from_file
from src.python_files.utils.submission_helpers import get_submission_keyboard, get_expired_keyboard, get_poll_keyboard, \
	format_text, encode_url


class TelegramPublisher:
	_TESTING: bool = False
	TEST_CHANNEL_ID: int = get_chat_id_from_file(DIR.CHANNEL_TEST)
	GROUP_ID: int = get_chat_id_from_file(DIR.GROUP_TEST)
	LIVE_CHANNEL_ID: int = get_chat_id_from_file(DIR.CHANNEL_MACROMICROITALIA)

	def __init__(self, application: Application) -> None:
		self._bot: ExtBot = application.bot

	@property
	def channel_id(self) -> int:
		"""Restituisce l'ID del canale corretto in base allo stato di testing."""
		return self.TEST_CHANNEL_ID if self._TESTING else self.LIVE_CHANNEL_ID

	def _get_chat_id(self, chat_type: ChatType) -> int:
		"""Risolve la chat di destinazione (Gruppo vs Canale Test/Live)."""
		if chat_type == ChatType.GROUP:
			return self.GROUP_ID
		return self.channel_id

	@error_origin()
	async def send_submission(self, submission: Submission, chat_type: ChatType) -> TelegramMessage | None:
		text: str = format_text(submission=submission, chat=chat_type)
		if not submission.channel_photo:
			await prepare_img_to_send(image=submission.image)

		photo:str = encode_url(submission.get_photo_url(chat_type))
		chat_id:int = self._get_chat_id(chat_type)
		keyboard: InlineKeyboardMarkup = get_submission_keyboard(submission=submission, chat_type=chat_type)

		try:
			message:TelegramMessage = await self._bot.send_photo(
				chat_id=chat_id,
				caption=text,
				photo=photo,
				reply_markup=keyboard,
				parse_mode=ParseMode.MARKDOWN_V2,
			)

			if chat_type == ChatType.GROUP:
				submission.group_message_id = message.message_id
			elif chat_type == ChatType.CHANNEL:
				submission.status = STATUS.SENT
				submission.channel_message_id = message.message_id

				try:
					await self._bot.delete_message(
						chat_id=self.GROUP_ID,
						message_id=submission.group_message_id
					)

				except Exception as e:
					print(f"Errore durante l'eliminazione del messaggio {submission.image_id}\n\n{e}")
					await self._bot.edit_message_reply_markup(
						chat_id=self.GROUP_ID,
						message_id=submission.group_message_id,
						reply_markup=get_expired_keyboard()
					)

			SubmissionDAO.update_submission(submission=submission)
			return message

		except Exception:
			print(f"ERRORE Submission {submission.image_id}")
			return None

	@error_origin()
	async def send_poll(self, poll: list[str], chat_type: ChatType) -> TelegramMessage | None:
		chat_id: int = self._get_chat_id(chat_type)
		is_anonymous: bool = (chat_type == ChatType.CHANNEL)

		try:
			domanda: str = f"{poll[0].strip('?')}?"
			risposte: list[str] = poll[1:]
			keyboard: InlineKeyboardMarkup|None = get_poll_keyboard(chat_type=chat_type)

			return await self._bot.send_poll(
			   chat_id=chat_id,
			   question=domanda,
			   options=risposte,
			   is_anonymous=is_anonymous,
			   reply_markup=keyboard,
			  )
		except Exception as e:
			print(f"Errore durante la creazione del sondaggio!\n\n{e}")
			return None