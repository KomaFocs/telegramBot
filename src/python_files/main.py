import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from src.python_files.commands.handle_message import handle_message
from src.python_files.config.lista_comandi import COMANDI
from src.python_files.errors.error import error
from src.python_files.jobs.backup import backup_periodico
from src.python_files.jobs.post_init import avviamento
from src.python_files.jobs.shutdown import gestisci_shutdown
from src.python_files.utils.util import DIR

BOT_TOKEN = open(DIR.TOKEN_FILE, "r").read().strip()

if __name__ == "__main__":
	oggi:datetime.date = datetime.date.today()
	print(f"Bot in avviamento - {oggi.day}/{oggi.month}/{oggi.year}\n")

	app = (
		Application.builder()
		.token(BOT_TOKEN)
		.post_init(avviamento)
		.post_shutdown(gestisci_shutdown)
		.build()
	)

	# Commands
	for comando, (funzione, _) in COMANDI.items():
		app.add_handler(CommandHandler(comando, funzione))

	# Messages
	app.add_handler(MessageHandler(filters.TEXT, handle_message))

	# Error
	app.add_error_handler(error)

	# Backup
	backup_periodico(app, False)  # cambia in True per attivare i backup

	# Check for messages every <tot> seconds
	print("Bot pronto. In attesa dei messaggi...")
	app.run_polling(allowed_updates=[Update.MESSAGE, Update.CALLBACK_QUERY],poll_interval=2)


