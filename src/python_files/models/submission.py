from __future__ import annotations

from dataclasses import dataclass
from src.python_files.models.user import User
from src.python_files.models.image import Image
from src.python_files.models.message import Message


@dataclass
class Submission:
	user: User
	image: Image
	message: Message

	@classmethod
	def from_message(cls,message: Message,image: Image,user: User) -> Submission:
		return cls(
			user=user,
			image=image,
			message=message,
		)