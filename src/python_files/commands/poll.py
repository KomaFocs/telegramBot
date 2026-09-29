from telegram import Update, Message as TelegramMessage
from telegram.constants import ParseMode, ChatType
from telegram.ext import ContextTypes

from src.python_files.jobs.telegram_publisher import TelegramPublisher
from src.python_files.utils.constants import DIR
from src.python_files.utils.decorators import logger, single_execution
from src.python_files.utils.telegram_helpers import codice_inline, grassetto, sottolineato


@logger
@single_execution()
async def poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> TelegramMessage | None:
	_MINIMO:int = 3
	user_id:str = str(update.effective_user.id)
	admins:list[str] = []
	with open(DIR.ADMINS, "r") as file:
		for line in file.readlines():
			admins.append(line.strip())

	if not admins:
		return None

	if user_id not in admins:
		# FIXME: gestire i pezzenti
		return None

	if not context.args:
		msg = (
			f"Per creare un sondaggio devi scrivere: {codice_inline('/sondaggio <domanda>')} ? {codice_inline('<risposta 1> <risposta 2>')}\n"
			f"Esempio: {grassetto('/sondaggio dove si trova Roma? Lazio Molise Campania Piemonte')}\n\n"
			f"Importante: la prima risposta {grassetto('deve')} essere quella {sottolineato('corretta')}"
		)
		await update.message.reply_text(
			text=msg,
			parse_mode=ParseMode.MARKDOWN_V2,
		)
		return None

	raw:str = " ".join(context.args)
	if "?" not in raw:
		await update.message.reply_text("Inserisci un punto di domanda '?' per separare domanda e opzioni!")
		return None

	parts:list[str] = ([
		raw.split("?", 1)[0].strip() + "?"] +
		raw.split("?", 1)[1].split()
	)

	if len(parts) < _MINIMO:
		await update.message.reply_text("Servono almeno una domanda e due opzioni per creare un sondaggio!")
		return None

	publisher:TelegramPublisher = TelegramPublisher(context.application)
	m:TelegramMessage = await publisher.send_poll(poll=parts,chat_type=ChatType.GROUP)
	return m


