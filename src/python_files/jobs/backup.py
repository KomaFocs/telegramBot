from datetime import timedelta

from telegram.ext import ContextTypes, Application


async def salva_dati(target:Application | ContextTypes.DEFAULT_TYPE) -> None:
	app = target if isinstance(target, Application) else target.application
	# print(f"[{datetime.now():%d/%m/%Y - %H:%M:%S}]: backup eseguito.")


def backup_periodico(app:Application, active:bool = False) -> None:
	if active and app.job_queue:
		app.job_queue.run_repeating(
			salva_dati,
			interval=timedelta(minutes=60),
			first=timedelta(minutes=5),
		)
