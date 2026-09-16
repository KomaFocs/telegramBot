from datetime import timedelta

from telegram.ext import ContextTypes, Application

from src.python_files.config.database import backup_database
from src.python_files.utils.constants import DIR
from src.python_files.utils.log import time_log


async def salva_dati(app:Application | ContextTypes.DEFAULT_TYPE) -> None:
	# app:Application = app if isinstance(app, Application) else app.application
	backup_database(database_path=DIR.DATABASE, backup_dir=DIR.BACKUP_FILES)
	time_log("Backup Database")


def backup_periodico(app:Application, active:bool) -> None:
	if active and app.job_queue:
		app.job_queue.run_repeating(
			salva_dati,
			interval=timedelta(minutes=60*4),
			first=timedelta(minutes=5),
		)
