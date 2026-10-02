from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

from telegram.constants import ChatType

from src.python_files.models.user import User
from src.python_files.models.image import Image
from src.python_files.models.message import Message
from src.python_files.utils.constants import STATUS


@dataclass
class Submission:
	user: User
	image: Image
	message: Message

	@property
	def image_id(self) -> int:
		return self.image.image_id

	@property
	def scheduled_at(self) -> datetime|None:
		return self.message.scheduled_at

	@scheduled_at.setter
	def scheduled_at(self, value:datetime|None) -> None:
		self.message.scheduled_at = value

	@property
	def status(self) -> STATUS:
		return self.message.status

	@property
	def status_text(self) -> str:
		match self.status:
			case STATUS.PENDING:
				return "Da approvare"
			case STATUS.APPROVED:
				return "Approvato"
			case STATUS.REJECTED:
				return "Rifiutato"
			case STATUS.SENT:
				return "Inviato"

			case _:
				return self.status

	@property
	def name_user(self) -> str:
		"""Restituisce il display_name dell'utente; se non lo trova, restituisce lo username"""
		return (
			self.user.display_name
			if self.user.display_name
			else self.user.username
		)

	@status.setter
	def status(self, value:STATUS) -> None:
		self.message.status = value

	@property
	def group_message_id(self) -> int|None:
		return self.message.sent_in_group

	@group_message_id.setter
	def group_message_id(self, value:int) -> None:
		self.message.sent_in_group = value

	@property
	def channel_message_id(self) -> int|None:
		return self.message.channel_message_id

	@channel_message_id.setter
	def channel_message_id(self, value:int) -> None:
		self.message.channel_message_id = value

	@property
	def channel_photo(self) -> str|None:
		return self.image.hd_image_link

	@channel_photo.setter
	def channel_photo(self, value:str) -> None:
		self.image.hd_image_link = value

	@property
	def group_photo(self) -> str:
		return self.image.sd_image_link

	@group_photo.setter
	def group_photo(self, value:str) -> None:
		self.image.sd_image_link = value


	def get_photo_url(self, chat_type:ChatType) -> str:
		return (
			self.group_photo
			if chat_type == ChatType.GROUP
			else self.channel_photo
		)

	@classmethod
	def from_message(cls, message: Message) -> Submission|None:

		if not message or not message.image or not message.image.user:
			img_id = getattr(message, "image_id", "null")
			print(f"Immagine mancante al messaggio {img_id}")
			return None

		return Submission(
			image=message.image,
			message=message,
			user=message.image.user
		)

	def __str__(self) -> str:
		attrs:str = "\n".join(
			_ for _ in (
				f"image_id:{self.image_id}",
				f"user:{self.name_user}",
				f"SD_link:{self.image.sd_image_link}",
				f"HD_link:{self.image.hd_image_link}",
				f"submission_link:{self.image.submission_link}",
				f"scheduled_at:{self.scheduled_at}"
			)
		)
		return f"{self.__class__.__name__}({attrs})"