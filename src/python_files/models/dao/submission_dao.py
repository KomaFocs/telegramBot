from typing import overload, Sequence

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.python_files.config.database import get_session
from src.python_files.models.image import Image
from src.python_files.models.message import Message
from src.python_files.models.submission import Submission
from src.python_files.utils.constants import STATUS
from src.python_files.utils.decorators import integrity_error


class SubmissionDAO:

	@overload
	@staticmethod
	def _to_submission(data:None) -> None:
		...

	@overload
	@staticmethod
	def _to_submission(data:Message) -> Submission|None:
		...

	@overload
	@staticmethod
	def _to_submission(data:Sequence[Message]) -> list[Submission]:
		...

	@staticmethod
	def _to_submission(data:Message|Sequence[Message]|None) -> Submission|list[Submission]|None:
		"""Converte oggetti Message in Submission filtrando eventuali record non validi o orfani."""
		if data is None:
			return None

		if isinstance(data, (list, tuple, Sequence)):
			return [
				sub for m in data
				if (sub := Submission.from_message(m)) is not None
			]

		return Submission.from_message(data)


	@staticmethod
	def get_submission_by_id(image_id:int) -> Submission | None:
		with get_session() as session:
			statement = (
				select(Message)
				.options(joinedload(Message.image).joinedload(Image.user))
				.where(Message.image_id == image_id)
			)
			message = session.scalar(statement)

			if message is None:
				return None

			return SubmissionDAO._to_submission(message)


	@staticmethod
	@integrity_error
	def add_submission(submission:Submission) -> None:
		with get_session() as session:
			session.merge(submission.user)
			session.merge(submission.image)
			session.merge(submission.message)
			session.commit()


	@staticmethod
	def update_submission(submission:Submission, status:STATUS=None, sent_in_group:bool=None, ch_msg_id:int=None) -> None:
		if status is not None:
			submission.status = status

		if sent_in_group is not None:
			submission.message.sent_in_group = sent_in_group

		if ch_msg_id is not None:
			submission.message.channel_message_id = ch_msg_id

		with get_session() as session:
			session.merge(submission.user)
			session.merge(submission.image)
			session.merge(submission.message)
			session.commit()


	@staticmethod
	def delete_submission(image_id:int) -> None:
		with get_session() as session:
			message = session.get(Message, image_id)
			image = session.get(Image, image_id)

			if message:
				session.delete(message)
			if image:
				session.delete(image)

			session.commit()


	@staticmethod
	def get_submissions(scheduled:bool) -> list[Submission]:
		"""Restituisce una lista di messaggi.
		:param scheduled: stabilisce quali messaggi restituire.
		True -> messaggi programmati da inviare sul canale.
		False -> messaggi non ancora programmati.
		"""
		with get_session() as session:
			statement = (
				select(Message)
				.options(joinedload(Message.image).joinedload(Image.user))
				.where(Message.status.in_([STATUS.PENDING, STATUS.APPROVED]))
			)

			if scheduled:
				# CANALE: deve essere stato inviato nel gruppo E avere una data
				statement = statement.where(
					Message.sent_in_group == True,
					Message.scheduled_at.is_not(None)
				).order_by(Message.scheduled_at.asc())
			else:
				# GRUPPO: qualsiasi messaggio non ancora inviato nel gruppo
				statement = statement.where(
					Message.sent_in_group == False
				).order_by(Message.image_id.asc())

			messages = session.scalars(statement).unique().all()
			return SubmissionDAO._to_submission(messages)


	@staticmethod
	def get_all_submissions(status:list[STATUS]|None = None) -> list[Submission]:
		with get_session() as session:
			statement = (
				select(Message)
				.options(joinedload(Message.image).joinedload(Image.user))
			)

			if status:
				statement = statement.where(Message.status.in_(status))

			messages = session.scalars(statement).unique().all()
			return SubmissionDAO._to_submission(messages)


	@staticmethod
	def reset_pending_group_submissions() -> None:
		"""Resetta il flag 'sent_in_group' a False per tutti i messaggi nel DB non inviati nel canale"""
		with get_session() as session:
			statement = (
				select(Message)
				.where(
					Message.sent_in_group == True,
					Message.channel_message_id.is_(None),
				)
			)
			messages = session.scalars(statement).all()

			for message in messages:
				message.sent_in_group = False

			session.commit()


	@staticmethod
	def reset_all() -> None:
		f"""
		Resetta i messaggi con {STATUS.SENT} o {STATUS.APPROVED} a\n
		1) {STATUS.PENDING}
		2) sent_in_group = {False}
		3) channel_message_id = {None}
		"""
		with get_session() as session:

			statement = (
				select(Message)
			)
			messages = session.scalars(statement).all()

			for message in messages:
				message.sent_in_group = False
				message.status = STATUS.PENDING
				message.scheduled_at = None
				message.channel_message_id = None

			session.commit()
