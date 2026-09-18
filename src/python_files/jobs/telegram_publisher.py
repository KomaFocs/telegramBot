import asyncio

from telegram import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.constants import ChatType
from telegram.error import BadRequest, RetryAfter
from telegram.ext import Application, ExtBot

from src.python_files.commands.handlers.handle_message import handle_message
from src.python_files.models.image import Image
from src.python_files.models.submission import Submission
from src.python_files.models.user import User
from src.python_files.utils.constants import DIR, FA_URL
from src.python_files.utils.fa_client import prepare_img_to_send
from src.python_files.utils.telegram_helpers import get_chat_id_from_file, format_text, confirm_reject_keyboard


class TelegramPublisher:
	GROUP_ID:int = get_chat_id_from_file(DIR.GROUP_TEST)
	CHANNEL_ID:int = get_chat_id_from_file(DIR.CHANNEL_TEST)

	def __init__(self, application: Application) -> None:
		self._bot: ExtBot = application.bot

	@staticmethod
	def _configure_keyboard(submission:Submission, chat:ChatType) -> InlineKeyboardMarkup:
		user:User = submission.user
		image:Image = submission.image

		if chat == ChatType.CHANNEL:
			return InlineKeyboardMarkup([
				[
					InlineKeyboardButton(
					text=f"{user.display_name}", url=f"{user.link}"
					),
					InlineKeyboardButton(
						text=f"🔗 Apri il link", url=f"{image.submission_link}"
					)
				]
			])
		else:
			return InlineKeyboardMarkup([
				[
					InlineKeyboardButton(
						text=f"Status: {submission.message.status}", callback_data="None"
					),
					confirm_reject_keyboard(image_id=image.image_id)
				]
			])


	async def send_message(self, submission:Submission, chat:ChatType) -> Message:
		text:str = format_text(submission=submission, chat=chat)
		image:Image = await prepare_img_to_send(submission.image)
		photo:str
		chat_id:int
		keyboard:InlineKeyboardMarkup = self._configure_keyboard(chat)

		if chat == ChatType.GROUP:
			photo = image.sd_image_link
			chat_id = self.GROUP_ID
		else:
			photo = image.hd_image_link
			chat_id = self.CHANNEL_ID

		return await self._bot.send_photo(
			chat_id=chat_id,
			caption=text,
			photo=photo,
			reply_markup=keyboard
		)
