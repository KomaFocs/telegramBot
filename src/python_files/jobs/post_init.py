import asyncio

from telegram import BotCommand, Bot, InputProfilePhotoStatic
from telegram.error import RetryAfter
from telegram.ext import Application

from src.python_files.config.lista_comandi import COMANDI
from src.python_files.config.database import init_db
from src.python_files.jobs.job_queue import JobQueue
from src.python_files.jobs.telegram_publisher import TelegramPublisher
from src.python_files.utils.constants import DIR, JOB_QUEUE, JOB_QUEUE_TASK
from src.python_files.utils.log import time_log


async def avviamento(application:Application):
	bot:Bot = application.bot
	commands = [BotCommand(cmd, descr) for cmd, (_, descr) in COMANDI.items()]
	time_log("Comandi impostati")
	await bot.set_my_commands(commands)

	try:
		with open(DIR.IMG_FILES / "square_astley.jpg", "rb") as photo:
			await bot.set_my_profile_photo(
				photo=InputProfilePhotoStatic(
					photo=photo
				)
			)

	except RetryAfter as e:
		msg:str = f"Rate limit: riprova ad aggiornare la foto profilo fra {e.retry_after} secondi."
		time_log(msg)

	init_db()
	setup_job(application)

	time_log("Avvio completato.")


def setup_job(application:Application):
	publisher:TelegramPublisher = TelegramPublisher(application)
	job_queue:JobQueue = JobQueue(publisher)

	application.bot_data[JOB_QUEUE] = job_queue

	task:asyncio.Task = asyncio.create_task(job_queue.run())

	application.bot_data[JOB_QUEUE_TASK] = task
