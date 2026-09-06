import asyncio
import random
from telegram.constants import ChatAction
from src.python_files.utils.constants import DIR, DEFAULT_STUN_DURATION, HIOSHIRU_FILE, DELETE_INCOMING_MESSAGES
from src.python_files.utils.cooldown import stun_bot
from src.python_files.utils.decorators import logger, chat_action, single_execution
from telegram import Update, Message, Chat
from telegram.ext import ContextTypes
from src.python_files.utils.telegram_helpers import resume_operations


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
		case Nome_Comandi.GUIDA:
			if random.randint(1, 10) < 9:
				reply = Istruzioni.GUIDA
			else:
				await impazzisci(update=update, context=context)
				return
		case Nome_Comandi.FURAFFINITY: reply = Istruzioni.FURAFFINITY
		case Nome_Comandi.SUBMISSIONS: reply = Istruzioni.SUBMISSIONS
		case _: reply = Istruzioni.SBAGLIATO

	await update.message.reply_text(reply, parse_mode="HTML")


@single_execution(verbose=False)
async def impazzisci(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	WAIT_TIMES: list[int] = [3, 6]
	chat: Chat | None = update.effective_chat
	user = update.effective_user
	if not chat or not user:
		return

	context.user_data[DELETE_INCOMING_MESSAGES] = True

	with open(DIR.SECRETS / HIOSHIRU_FILE, "r") as f:
		stickers = [line.strip().split("_")[-1] for line in f if line.strip()]

	sticker_iterator = iter(stickers)
	sticker_prefix: str = "sticker_"

	messages: list[str] = [
		"Richiesta ricevuta: /guida guida\n\n"
		"Questo non lo avevo previsto, ora consulto la guida per sapere come consultare la guida.--",
		"\n\nAspetta... ho bisogno di sapere come consultare la guida per consultare la guida...",
		f"{sticker_prefix}{next(sticker_iterator)}",
		"Mi stai chiedendo informazioni sulle informazioni... mi stai chiedendo come funziona "
		"il comando che hai usato per chiedere informazioni sul comando.",
		f"{sticker_prefix}{next(sticker_iterator)}",
		"Ok, vuoi una guida sulla guida.--",
		"\n\nDevo usare la guida per capire come usare la guida usando la guida per spiegarti come usare la guida...",
		"Tentativo di consultare la guida in corso... attendere prego...",
		"Attenzione! Guida in surriscaldamento: consultare la guida prima di consultare la guida.--",
		"\n\nAttenzione: surriscaldamento del surriscaldamento, consigliamo di consultare la guida su come smettere di consultare la guida.",
		f"{sticker_prefix}{next(sticker_iterator)}",
		"\n\nAttenzione: messaggio 'attenzione' in surriscaldamento.",
		f"Stiamo avendo problemi tecnici. Riprova fra {DEFAULT_STUN_DURATION} secondi.",
		f"{sticker_prefix}{next(sticker_iterator)}",
	]

	to_delete: list[Message] = []
	last_message: Message | None = None
	last_text: str = ""

	try:
		for text in messages:
			if text.startswith(sticker_prefix):
				sticker_id = text.removeprefix(sticker_prefix)

				await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.CHOOSE_STICKER)
				await asyncio.sleep(WAIT_TIMES[0])

				sent_msg = await context.bot.send_sticker(chat_id=chat.id, sticker=sticker_id)
				to_delete.append(sent_msg)

				last_message = None
				last_text = ""

			elif last_message and last_text.endswith("--"):
				await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
				await asyncio.sleep(random.uniform(*WAIT_TIMES))

				base_text = last_text.removesuffix("--")
				clean_addition = text.removesuffix("--") if text.endswith("--") else text

				updated_text = f"{base_text}{clean_addition}"
				await last_message.edit_text(updated_text)

				last_text = f"{base_text}{text}"

			else:
				to_send: str = text.removesuffix("--") if text.endswith("--") else text

				await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
				await asyncio.sleep(random.uniform(*WAIT_TIMES))

				sent_msg = await context.bot.send_message(chat_id=chat.id, text=to_send)
				to_delete.append(sent_msg)

				last_message = sent_msg
				last_text = text

		stun_bot(context, user.id, duration=DEFAULT_STUN_DURATION)
		asyncio.create_task(resume_operations(update=update, context=context, messages=to_delete, delay=DEFAULT_STUN_DURATION))

	finally:
		context.user_data[DELETE_INCOMING_MESSAGES] = False
