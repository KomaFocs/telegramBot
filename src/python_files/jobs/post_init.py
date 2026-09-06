from datetime import datetime
from telegram import BotCommand, Bot, InputProfilePhotoStatic
from telegram.ext import Application

from src.python_files.config.lista_comandi import COMANDI
from src.python_files.utils.constants import DIR


async def avviamento(application:Application):
	bot:Bot = application.bot
	commands = [BotCommand(cmd, descr) for cmd, (_, descr) in COMANDI.items()]
	print(f"[{datetime.now():%d/%m/%Y - %H:%M:%S}]: Comandi impostati.")
	await bot.set_my_commands(commands)

	with open(DIR.IMG_FILES/"square_astley.jpg", "rb") as photo:
		await bot.set_my_profile_photo (
			photo = InputProfilePhotoStatic (
				photo = photo
			)
		)

	print(f"[{datetime.now():%d/%m/%Y - %H:%M:%S}]: Avvio completato.")

