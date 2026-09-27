from telegram import Message as TelegramMessage, InlineKeyboardMarkup
from telegram.constants import ChatType
from telegram.ext import Application, ExtBot

from src.python_files.models.dao.submission_dao import SubmissionDAO
from src.python_files.models.image import Image
from src.python_files.models.submission import Submission
from src.python_files.utils.constants import DIR, STATUS
from src.python_files.utils.fa_client import prepare_img_to_send
from src.python_files.utils.telegram_helpers import get_chat_id_from_file, format_text, get_submission_keyboard


class TelegramPublisher:
	GROUP_ID:int = get_chat_id_from_file(DIR.GROUP_TEST)
	CHANNEL_ID:int = get_chat_id_from_file(DIR.CHANNEL_TEST)

	def __init__(self, application:Application) -> None:
		self._bot: ExtBot = application.bot


	async def send_submission(self, submission:Submission, chat_type:ChatType) -> TelegramMessage|None:
		text:str = format_text(submission=submission, chat=chat_type)
		image:Image = submission.image \
			if submission.image.hd_image_link \
			else await prepare_img_to_send(submission.image)
		photo:str
		chat_id:int
		keyboard:InlineKeyboardMarkup = get_submission_keyboard(submission=submission, chat_type=chat_type)

		if chat_type == ChatType.GROUP:
			photo = image.sd_image_link
			chat_id = self.GROUP_ID
		else:
			photo = image.hd_image_link
			chat_id = self.CHANNEL_ID

		try:
			message:TelegramMessage = await self._bot.send_photo(
				chat_id=chat_id,
				caption=text,
				photo=photo,
				reply_markup=keyboard
			)
			if chat_type == ChatType.GROUP:
				submission.message.sent_in_group = True
			elif chat_type == ChatType.CHANNEL:
				submission.status = STATUS.SENT
				submission.message.channel_message_id = message.message_id

			SubmissionDAO.update_submission(submission=submission)
			return message

		except Exception as e:
			print(f"ERRORE Submission {submission.image.image_id}\n\n{e}")
			return None


	async def send_text_message(self, text, chat_type:ChatType) -> None:
		chat_id = (
			self.CHANNEL_ID
			if chat_type == ChatType.CHANNEL
			else self.GROUP_ID
		)

		await self._bot.send_message(
			text=text,
			parse_mode="markdown",
			chat_id=chat_id
		)
