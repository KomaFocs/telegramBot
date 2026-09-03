from src.python_files.utils.decorators import logger, chat_action
from telegram import Update
from telegram.ext import ContextTypes


@logger
@chat_action()
async def guida_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	cmd:str = context.args[0].lower().lstrip("/") if context.args else ""
	reply:str = ""

	from src.python_files.config.lista_comandi import Nome_Comandi

	if cmd == "":
		reply = (
			"ℹ️ Questo comando ti spiegherà come si usano gli altri comandi del bot.\n"
			f"Se vuoi info su un comando, scrivi: <code>/{Nome_Comandi.GUIDA} nome_comando</code>\n\n"
			f"Ad esempio: <code>/{Nome_Comandi.GUIDA} {Nome_Comandi.IMG}</code>"
		)
		await update.message.reply_text(reply, parse_mode="HTML")
		return

	class Istruzioni:
		START = (
			f"/{Nome_Comandi.START} si usa per avviare i bot su Telegram. Viene eseguito automaticamente quando premi 'avvio' la prima volta. "
			"Stai parlando con me, sono già avviato: non c'è motivo di usarlo nuovamente."
		)
		IMG = (
			f"Con /{Nome_Comandi.IMG} io ti invierò una foto."
		)
		MEGLIO = (
			f"/{Nome_Comandi.MEGLIO} serve a far capire alle persone cos'è meglio *davvero*."
		)
		GUIDA = (
			"ಠ_ಠ"
		)
		FURAFFINITY = (
			f"/{Nome_Comandi.FURAFFINITY} ti permette di cercare un'immagine pubblicata su FA e vederla comodamente qui in chat.\n"
			"Opzionalmente puoi aggiungere un link al comando:\n\n"
			f"<code>/{Nome_Comandi.FURAFFINITY} furrafinity.net/view/...</code>\n\n\nImportante: dammi sempre un link con un view/id, "
			"altrimenti potrei darti un risultato diverso da ciò che ti aspettavi!"
		)
		SUBMISSIONS = (
			"Comando riservato a Pianostrong e Koma, per favore non usarlo ^^.\n"
		)
		SBAGLIATO = (
			"Non riconosco questo comando ^^"
		)

	match cmd:
		case Nome_Comandi.START: reply = Istruzioni.START
		case Nome_Comandi.IMG: reply = Istruzioni.IMG
		case Nome_Comandi.MEGLIO: reply = Istruzioni.MEGLIO
		case Nome_Comandi.GUIDA: reply = Istruzioni.GUIDA
		case Nome_Comandi.FURAFFINITY: reply = Istruzioni.FURAFFINITY
		case Nome_Comandi.SUBMISSIONS: reply = Istruzioni.SUBMISSIONS
		case _: reply = Istruzioni.SBAGLIATO

	await update.message.reply_text(reply, parse_mode="HTML")