from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

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
	def scheduled_at(self) -> datetime | None:
		return self.message.scheduled_at

	@scheduled_at.setter
	def scheduled_at(self, value: datetime | None) -> None:
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
	def name_user(self):
		return (
			self.user.display_name
			if self.user.display_name
			else self.user.username
		)

	@status.setter
	def status(self, value: STATUS) -> None:
		self.message.status = value

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