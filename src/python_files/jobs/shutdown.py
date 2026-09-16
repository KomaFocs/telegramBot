import asyncio

from telegram import Bot
from telegram.error import RetryAfter
from telegram.ext import Application
from src.python_files.jobs.backup import salva_dati
from src.python_files.jobs.job_queue import JobQueue
from src.python_files.utils.constants import JOB_QUEUE, JOB_QUEUE_TASK
from src.python_files.utils.log import time_log


async def gestisci_shutdown(app:Application) -> None:
	print("Bot in spegnimento...")
	bot:Bot = app.bot
	try:
		job_queue:JobQueue = app.bot_data[JOB_QUEUE]
		task:asyncio.Task = app.bot_data[JOB_QUEUE_TASK]

		job_queue.stop()

		await task

		await bot.remove_my_profile_photo()
		await salva_dati(app)

	except RetryAfter as retry:
		msg = f"Rate limit! Riprova fra {retry.retry_after} secondi."
		time_log(msg)