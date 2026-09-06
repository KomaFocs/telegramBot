from telegram import Bot
from telegram.ext import Application
from src.python_files.jobs.backup import salva_dati


async def gestisci_shutdown(app:Application) -> None:
	print("Bot in spegnimento...")
	bot:Bot = app.bot
	await bot.remove_my_profile_photo()
	await salva_dati(app)