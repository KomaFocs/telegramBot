import asyncio
from asyncio import Event
from datetime import date, datetime, timedelta

from src.python_files.jobs.telegram_publisher import TelegramPublisher
from src.python_files.models.dao.message_dao import (
	get_messages,
	update_message,
)
from src.python_files.models.message import Message
from src.python_files.models.submission import Submission
from src.python_files.utils.constants import ORARI, STATUS


class JobQueue:
	BATCH_SIZE: int = 5

	def __init__(self, publisher: TelegramPublisher) -> None:
		self._publisher:TelegramPublisher = publisher
		self._event:Event = asyncio.Event()
		self._running:bool = True
		self._queue:list[Message] = []

	def stop(self) -> None:
		self._running = False
		self._event.set()

	def notify(self) -> None:
		self._event.set()

	async def run(self) -> None:
		await self._recover_queue()

		while self._running:
			if not self._queue:
				self._queue = self._next_batch()

			if not self._queue:
				await self._event.wait()
				self._event.clear()
				continue

			message:Message = self._queue[0]
			if message.scheduled_at is None:
				continue

			delay = (message.scheduled_at - datetime.now()).total_seconds()

			try:
				await asyncio.wait_for(
					self._event.wait(),
					timeout=max(0.0, delay),
				)
				self._event.clear()

			# Nota bene:
			# quando asyncio.wait_for() termina, lancia TimeoutError
			# Non è un eccezione nel senso di errore, bensì un comportamento atteso
			except asyncio.TimeoutError:
				submission = self._get_submission(message)
				if submission is not None:
					await self._execute(submission)
				self._queue.pop(0)

	async def _recover_queue(self) -> None:
		messages: list[Message] = get_messages(scheduled=True)
		now: datetime = datetime.now()

		for message in messages:
			if message.scheduled_at is not None and message.scheduled_at <= now:
				submission = self._get_submission(message)
				if submission is not None:
					await self._execute(submission)
				else:
					message.scheduled_at = None
					update_message(message)

	def _next_batch(self) -> list[Message]:
		"""Restituisce una lista di messaggi.
		Se non ci sono messaggi da inviare al canale, genera un nuovo batch di messaggi."""
		messages: list[Message] = get_messages(scheduled=True)
		if messages:
			return messages

		messages: list[Message] = get_messages(scheduled=False)
		if not messages:
			return []

		batch = messages[:self.BATCH_SIZE]
		slots = self._get_available_slots(len(batch))

		for message, scheduled_at in zip(batch, slots):
			message.scheduled_at = scheduled_at

			submission = self._get_submission(message)
			if submission is None:
				continue

			#await self._publisher.send_to_group(submission)
			message.sent_in_group = True
			update_message(message)

		return batch

	async def _execute(self, submission: Submission) -> None:
		"""Esegue solo l'invio al canale e l'aggiornamento dello stato."""
		await self._publisher.send_to_channel(submission)

		submission.message.status = STATUS.SENT
		submission.message.scheduled_at = None
		update_message(submission.message)

	@staticmethod
	def _get_available_slots(count: int) -> list[datetime]:
		"""Restituisce una lista di slot disponibili."""
		occupied: set[datetime] = {
			message.scheduled_at
			for message in get_messages(scheduled=True)
			if message.scheduled_at is not None and message.sent_in_group
		}

		slots: list[datetime] = []
		now = datetime.now()
		current_date: date = now.date()

		days_checked = 0
		max_days = 30

		while len(slots) < count and days_checked < max_days:
			for orario in ORARI:
				scheduled_at = datetime.combine(current_date, orario.value)

				if scheduled_at <= now:
					continue

				if scheduled_at in occupied:
					continue

				occupied.add(scheduled_at)
				slots.append(scheduled_at)

				if len(slots) == count:
					break

			current_date += timedelta(days=1)
			days_checked += 1

		return slots

	@staticmethod
	def _get_submission(message: Message) -> Submission | None:
		return (
			None
			if message.image is None or message.image.users is None
			else Submission(
				user=message.image.users,
				image=message.image,
				message=message,
			)
		)