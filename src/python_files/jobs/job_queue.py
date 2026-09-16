import asyncio
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
		self._publisher = publisher
		self._event = asyncio.Event()
		self._running = True

	def stop(self) -> None:
		self._running = False
		self._event.set()

	def notify(self) -> None:
		self._event.set()

	async def run(self) -> None:
		await self._recover_queue()

		while self._running:
			await self._start_next_batch()
			messages = get_messages(scheduled=True)

			if not messages:
				await self._event.wait()
				self._event.clear()
				continue

			message = messages[0]

			if message.scheduled_at is None:
				continue

			delay = (
					message.scheduled_at - datetime.now()
			).total_seconds()

			try:
				await asyncio.wait_for(
					self._event.wait(),
					timeout=max(0.0, delay),
				)
				self._event.clear()

			except asyncio.TimeoutError:
				submission = self._get_submission(message)

				if submission is not None:
					await self._execute(submission)

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
				break

	async def _start_next_batch(self) -> None:
		messages: list[Message] = get_messages(scheduled=False)

		if not messages:
			return

		batch = messages[:self.BATCH_SIZE]
		slots = self._get_available_slots(len(batch))

		for message, scheduled_at in zip(batch, slots):
			message.scheduled_at = scheduled_at

			submission = self._get_submission(message)
			if submission is None:
				continue

			await self._publisher.send_to_group(submission)
			message.sent_in_group = True
			update_message(message)

	@staticmethod
	def _get_next_message() -> Message | None:
		messages: list[Message] = get_messages(scheduled=True)

		for message in messages:
			if message.scheduled_at is not None:
				return message

		return None

	@staticmethod
	def _get_available_slots(count: int) -> list[datetime]:
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
				time_value = orario.value if hasattr(orario, "value") else orario
				scheduled_at = datetime.combine(
					current_date,
					time_value,
				)

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

	async def _execute(self, submission: Submission) -> None:
		await self._publisher.send_to_channel(submission)

		submission.message.status = STATUS.SENT
		submission.message.scheduled_at = None

		update_message(submission.message)

		remaining = get_messages(scheduled=True)

		if not remaining:
			await self._start_next_batch()