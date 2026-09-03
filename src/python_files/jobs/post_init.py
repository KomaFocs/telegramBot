from datetime import datetime
from telegram import BotCommand
from src.python_files.config.lista_comandi import COMANDI


async def avviamento(application):
	commands = [BotCommand(cmd, descr) for cmd, (_, descr) in COMANDI.items()]
	print(f"[{datetime.now():%d/%m/%Y - %H:%M:%S}]: Comandi impostati.")
	await application.bot.set_my_commands(commands)
	print(f"[{datetime.now():%d/%m/%Y - %H:%M:%S}]: Avvio completato.")
