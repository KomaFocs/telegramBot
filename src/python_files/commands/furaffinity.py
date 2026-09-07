import asyncio
import random, httpx
from telegram import Message, Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from src.python_files.config.lista_tipi import FA_Type
from src.python_files.utils.fa_client import send_request, get_images
from src.python_files.utils.decorators import logger, chat_action, single_execution
from src.python_files.utils.filters import check_for_blacklist, filter_submissions
from src.python_files.utils.telegram_helpers import check_url


@logger
@single_execution()
@chat_action()
async def furaffinity_command(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	# context.args[0]: url:str | ""
	msgs:list[str] = ["Ci sto lavorando", "Un attimo", "Richiesta ricevuta", "🤔"]
	status:Message = await update.message.reply_text(f"{random.choice(msgs)}...")

	categoria:str = FA_Type.ARTE.value
	query:str = "macro"
	link:str = f"https://www.furaffinity.net/search/?q={query}&mode=extended&type-{categoria}=1"
	try:
		if context.args:  # immagine scelta dall'utente
			link = check_url(context)
			if not link:
				await status.edit_text("Link non valido: devi fornire un link di furaffinity.")
				return

		response = await send_request(update=update, url=link)  # richiedi le foto
		if response is None:
			await status.edit_text("Errore nel ricevere info dal server.")
			return

		img = get_images(response)  # ottieni una lista in risposta
		images = filter_submissions(img)  # filtra secondo le regole
		if not images:
			await status.edit_text("Non ho trovato immagini valide.")
			return

		image = images[0]  # prendi l'unico elemento
		to_spoil, spoil_msg = check_for_blacklist(image.get_tags())  # controlla se c'è bisogno di usare lo spoiler
		full_text:str = f"{image.format_description()}{spoil_msg}"
		chat_id = update.effective_chat.id
		await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
		await asyncio.sleep(random.uniform(1,3))
		await context.bot.send_photo(
			chat_id=chat_id,
			photo=image.preview_link,
			has_spoiler=to_spoil,
			caption=full_text,
		)
		await status.delete()
	except httpx.HTTPStatusError as e:
		await status.edit_text(f"Errore HTTP - codice {e.response.status_code}. Riprova più tardi.")
	except httpx.RequestError:
		await status.edit_text("Impossibile raggiungere furaffinity.net. Verifica che la tua connessione sia attiva o che il sito sia online.")
	except TelegramError as e:
		await status.edit_text(f"È successo questo: {e.message}.")

	# Fine metodo