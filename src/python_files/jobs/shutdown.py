from telegram.ext import Application
from src.python_files.jobs.backup import salva_dati


async def gestisci_shutdown(app:Application) -> None:
	print("Bot in spegnimento...")
	await salva_dati(app)