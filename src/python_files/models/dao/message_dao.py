from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.python_files.config.database import get_session
from src.python_files.models.image import Image
from src.python_files.models.message import Message
from src.python_files.utils.constants import STATUS


def get_message(image_id:int) -> Message | None:
	with get_session() as session:
		return session.get(Message, image_id)


def add_message(messaggio:Message) -> None:
	with get_session() as session:
		session.add(messaggio)
		session.commit()


def get_messages(scheduled: bool) -> list[Message]:
	"""Restituisce una lista di messaggi.
	:param scheduled: stabilisce quali messaggi restituire.
		True -> messaggi programmati da inviare sul canale.
		False -> messaggi non ancora programmati.
	"""

	with get_session() as session:
		statement = (
			select(Message)
			.options(
				joinedload(Message.image).joinedload(Image.users)
			)
			.where(
				Message.status.in_([STATUS.PENDING, STATUS.APPROVED])
			)
		)

		if scheduled:
			# CANALE: deve essere stato inviato nel gruppo E avere una data
			statement = statement.where(
				Message.sent_in_group == True,
				Message.scheduled_at.is_not(None)
			).order_by(Message.scheduled_at.asc())
		else:
			# GRUPPO TEST: qualsiasi messaggio mai inviato nel gruppo
			statement = statement.where(
				Message.sent_in_group == False
			).order_by(Message.image_id.asc())

		return list(session.scalars(statement).unique().all())


def get_all_messages(status: list[STATUS] | None = None) -> list[Message]:
	with get_session() as session:
		statement = (
			select(Message)
			.options(
				joinedload(Message.image).joinedload(Image.users)
			)
		)

		if status:
			statement = statement.where(Message.status.in_(status))

		return list(session.scalars(statement).unique().all())


def reset_pending_group_messages() -> None:
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


def update_message(message:Message) -> None:
	with get_session() as session:
		session.merge(message)
		session.commit()
