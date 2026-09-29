import asyncio
import random
from asyncio import Event
from datetime import date, datetime, timedelta

from telegram.constants import ChatType
from telegram import Message as TelegramMessage
from src.python_files.jobs.telegram_publisher import TelegramPublisher

from src.python_files.utils.constants import ORARI, STATUS
from src.python_files.models.submission import Submission
from src.python_files.models.dao.submission_dao import SubmissionDAO


class JobQueue:
	BATCH_SIZE:int = 5

	def __init__(self, publisher: TelegramPublisher) -> None:
		self._publisher:TelegramPublisher = publisher
		self._event:Event = asyncio.Event()
		self._running:bool = True
		self._queue:list[Submission] = []


	def stop(self) -> None:
		self._running = False
		self._event.set()


	def notify(self) -> None:
		self._queue.clear()
		self._event.set()


	async def run(self) -> None:
		await self._recover_queue()

		while self._running:
			if not self._queue:
				self._queue = await self._next_batch()

			if not self._queue:
				await self._event.wait()
				self._event.clear()
				continue

			await self._notify_startup_status()

			submission:Submission = self._queue[0]
			if not submission.message or submission.message.scheduled_at is None:
				self._queue.pop(0)
				continue

			delay = (submission.message.scheduled_at - datetime.now()).total_seconds()

			try:
				await asyncio.wait_for(
					self._event.wait(),
					timeout=max(0.0, delay),
				)
				self._event.clear()

			# NOTA BENE: asyncio.wait_for() lancia TimeoutError al termine
			# Non è un errore, bensì un comportamento atteso
			except asyncio.TimeoutError:
				submission = SubmissionDAO.get_submission_by_id(submission.image_id)
				if (
					submission is not None and
					submission.message.status in [STATUS.PENDING, STATUS.APPROVED]
				):
					await self._execute(submission)
				if self._queue:
					self._queue.pop(0)


	async def _recover_queue(self) -> None:
		submissions:list[Submission] = SubmissionDAO.get_submissions(scheduled=True)
		now:datetime = datetime.now()

		expired:list[Submission] = sorted([
			sub
				for sub in submissions
				if sub
				and sub.message.scheduled_at is not None
				and sub.message.scheduled_at <= now
			],
			key=lambda sub: sub.message.scheduled_at or datetime.min
		)

		if not expired:
			return

		old:Submission = expired[0]
		await self._execute(old)

		remaining:list[Submission] = expired[1:]
		if remaining:
			slots:list[datetime] = self._get_available_slots(len(remaining))
			for sub, new_slot in zip(remaining, slots):
				sub.scheduled_at = new_slot
				SubmissionDAO.update_submission(sub)


	async def _next_batch(self) -> list[Submission]:
		"""Restituisce una lista di messaggi.
		Se non ci sono messaggi da inviare al canale, genera un nuovo batch di messaggi."""

		submissions:list[Submission] = SubmissionDAO.get_submissions(scheduled=True)

		if len(submissions) >= self.BATCH_SIZE:
			return sorted(submissions, key=lambda s: s.scheduled_at or datetime.min)[:self.BATCH_SIZE]

		attempted_ids:set[int] = set()

		while len(submissions) < self.BATCH_SIZE:
			required:int = self.BATCH_SIZE - len(submissions)
			all_unscheduled = SubmissionDAO.get_submissions(scheduled=False)
			unscheduled:list[Submission] = [
				s for s in all_unscheduled
				if s.image_id not in attempted_ids
			]
			if not unscheduled:
				break

			batch_candidates:list[Submission] = unscheduled[:required]
			slots:list[datetime] = self._get_available_slots(len(batch_candidates))
			added:bool = False

			for submission, scheduled_at in zip(batch_candidates, slots):
				attempted_ids.add(submission.image_id)
				submission.scheduled_at = scheduled_at

				try:
					res:TelegramMessage = await self._publisher.send_submission(submission, ChatType.GROUP)
					if res:
						submissions.append(submission)
						added = True

				except Exception as e:
					print(f"Errore per la submission {submission.image_id}\n\nStacktrace: {e}")
					submission.message.sent_in_group = None
					submission.scheduled_at = None

			if not added:
				break

		return sorted(submissions, key=lambda s: s.scheduled_at or datetime.min)


	async def _execute(self, submission: Submission) -> None:
		"""Esegue solo l'invio al canale e l'aggiornamento dello stato."""
		await self._publisher.send_submission(submission, ChatType.CHANNEL)


	@staticmethod
	def _get_available_slots(count: int) -> list[datetime]:
		"""Restituisce una lista di slot disponibili."""
		occupied: set[datetime] = {
			submission.scheduled_at
			for submission in SubmissionDAO.get_submissions(scheduled=True)
			if submission.scheduled_at
			and submission.message.sent_in_group
		}

		slots: list[datetime] = []
		now = datetime.now()
		current_date: date = now.date()

		days_checked = 0
		max_days = 30

		while len(slots) < count and days_checked < max_days:
			for orario in ORARI:
				scheduled_at = datetime.combine(current_date, orario.value)

				is_occupied = any(
					occ.date() == scheduled_at.date() and occ.hour == scheduled_at.hour
					for occ in occupied
				)

				if is_occupied:
					continue

				if scheduled_at <= now:
					continue

				offset_minutes:float = random.uniform(0,15)
				scheduled_at = scheduled_at + timedelta(minutes=offset_minutes)

				occupied.add(scheduled_at)
				slots.append(scheduled_at)

				if len(slots) == count:
					break

			current_date += timedelta(days=1)
			days_checked += 1
		return slots

	async def _notify_startup_status(self) -> None:
		"""Invia sul gruppo test i prossimi messaggi da inviare sul canale."""

		if not self._queue:
			return

		queue:list[Submission] = (
			self._queue[:self.BATCH_SIZE]
			if len(self._queue) > self.BATCH_SIZE
			else self._queue
		)

		for s in queue:
			if not s.message.sent_in_group:
				await self._publisher.send_submission(s, ChatType.GROUP)
