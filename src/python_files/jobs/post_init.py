import asyncio

from telegram import BotCommand, Bot, InputProfilePhotoStatic
from telegram.error import RetryAfter
from telegram.ext import Application

from src.python_files.config.database import init_db
from src.python_files.jobs.job_queue import JobQueue
from src.python_files.jobs.telegram_publisher import TelegramPublisher
from src.python_files.models.dao.submission_dao import SubmissionDAO
from src.python_files.models.submission import Submission
from src.python_files.utils.constants import DIR, JOB_QUEUE, JOB_QUEUE_TASK
from src.python_files.utils.fa_client import fetch_images_from_furaffinity
from src.python_files.utils.log import time_log


async def avviamento(application:Application):
	from src.python_files.config.lista_comandi import COMANDI
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


	# sequenza di avvio: database, recupero messaggi e scheduling
	await startup_sequence(application)

	time_log("Avvio completato.")



async def startup_sequence(application:Application) -> None:
	# configura database
	init_db()

	# controlla se ci sono messaggi già inviati nel gruppo ma non ancora mandati nel canale
	await check_pending_messages()

	# imposta la programmazione dei messaggi
	setup_job(application)


async def check_pending_messages() -> None:
	pending_submissions:list[Submission] = SubmissionDAO.get_submissions(scheduled=True)

	if not pending_submissions:
		# scarica nuove foto da FA e le salva nel DB
		await fetch_images_from_furaffinity()



def setup_job(application:Application):
	job_queue:JobQueue = JobQueue(TelegramPublisher(application))
	application.bot_data[JOB_QUEUE] = job_queue
	task:asyncio.Task = asyncio.create_task(job_queue.run())
	application.bot_data[JOB_QUEUE_TASK] = task
