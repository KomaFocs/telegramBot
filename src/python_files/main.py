from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, TypeHandler, CallbackQueryHandler
from telegram.request import HTTPXRequest

from src.python_files.commands.handlers.handle_callback import handle_callback
from src.python_files.commands.handlers.handle_message import handle_message
from src.python_files.commands.handlers.handle_sticker import handle_sticker
from src.python_files.commands.handlers.handle_ignore_channels import ignora_canali, debug
from src.python_files.commands.mini_app import open_app
from src.python_files.config.lista_comandi import COMANDI
from src.python_files.errors.error import error
from src.python_files.jobs.backup import backup_periodico
from src.python_files.jobs.post_init import avviamento
from src.python_files.jobs.pre_init import pre_init
from src.python_files.jobs.shutdown import gestisci_shutdown
from src.python_files.utils.cooldown import stunned
from src.python_files.config.commands_visibility import visibility
from src.python_files.utils.fa_client import DIR
from src.python_files.utils.log import time_log

with open(DIR.TOKEN_FILE, "r") as f:
	BOT_TOKEN = f.read().strip()

if __name__ == "__main__":
	time_log("Bot in avviamento...")

	custom_request = HTTPXRequest(
		connect_timeout=15.0,
		read_timeout=20.0,
		write_timeout=20.0,
		pool_timeout=15.0,
	)
	app = (
		Application.builder()
		.request(custom_request)
		.token(BOT_TOKEN)
		.post_init(avviamento)
		.post_stop(gestisci_shutdown)
		.concurrent_updates(True)
		.build()
	)

	# Ignora i messaggi nei canali
	app.add_handler(TypeHandler(Update, debug), group=-90)

	# Ignora i messaggi nei canali
	app.add_handler(TypeHandler(Update, ignora_canali), group=-10)

	# Comandi admin only
	app.add_handler(TypeHandler(Update, visibility), group=-2)

	# Stun
	app.add_handler(TypeHandler(Update, stunned), group=-1)

	# Callback pulsanti (approva/rifiuta...)
	app.add_handler(CallbackQueryHandler(handle_callback))

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

	pre_init()
	time_log("Bot pronto")

	# Controlla ogni tot secondi se arriva un nuovo messaggio
	app.run_polling(
		allowed_updates = Update.ALL_TYPES,
		drop_pending_updates = True,
		poll_interval = 1,
	)


