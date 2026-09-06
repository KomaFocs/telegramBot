from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, TypeHandler
from src.python_files.commands.handle_message import handle_message
from src.python_files.commands.handle_sticker import handle_sticker
from src.python_files.commands.mini_app import open_app
from src.python_files.config.lista_comandi import COMANDI
from src.python_files.errors.error import error
from src.python_files.jobs.backup import backup_periodico
from src.python_files.jobs.post_init import avviamento
from src.python_files.jobs.shutdown import gestisci_shutdown
from src.python_files.utils.cooldown import stunned
from src.python_files.utils.fa_client import DIR


with open(DIR.TOKEN_FILE, "r") as f:
	BOT_TOKEN = f.read().strip()

if __name__ == "__main__":
	print(f"[{datetime.now():%d/%m/%Y - %H:%M:%S}]: Bot in avviamento...")

	app = (
		Application.builder()
		.token(BOT_TOKEN)
		.post_init(avviamento)
		.post_shutdown(gestisci_shutdown)
		.build()
	)

	# Stun
	app.add_handler(TypeHandler(Update, stunned), group=-1)

	# Comandi
	for comando, (funzione, _) in COMANDI.items():
		app.add_handler(CommandHandler(comando, funzione))

	# Frontend
	app.add_handler(CommandHandler("app", open_app))

	# Messaggi
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

	# Sticker
	app.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))

	# Errori
	app.add_error_handler(error)

	# Backup
	backup_periodico(app, False)  # cambia in True per attivare i backup

	print(f"[{datetime.now():%d/%m/%Y - %H:%M:%S}]: Bot pronto.")

	# Controlla ogni tot secondi se arriva un nuovo messaggio
	app.run_polling(
		poll_interval = 2,
		allowed_updates = [Update.MESSAGE, Update.CALLBACK_QUERY],
		drop_pending_updates = True
	)


