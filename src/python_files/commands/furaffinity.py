import random, httpx
from bs4 import ResultSet
from telegram import Message, Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from src.python_files.config.lista_tipi import FA_Type
from src.python_files.utils.fa_client import (
	BeautifulSoup, send_request, parse_html_tag_image,
	get_uploader, get_image_tags, convert_tags_to_string, get_image_source
)
from src.python_files.utils.decorators import logger, chat_action, single_execution
from src.python_files.utils.filters import check_for_blacklist
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
		if not context.args:  # immagine a caso da FA
			response:BeautifulSoup|int = await send_request(link)

			# risultato di ricerca: immagine in SD e link relativo
			elements:ResultSet = response.select("b a")
			if not elements:
				await status.edit_text("Non ho trovato elementi nel link di tipo <a> nel link. Riprova.")
				return
			link = random.choice(elements).get("href")
			link = f"https://furaffinity.net{link}" if link.startswith("/") else link
			print("link: ", link)

		else:  # immagine scelta dall'utente
			link = check_url(context)
			if not link:
				await status.edit_text("Link non valido: devi fornire un link di furaffinity.")
				return

		response = await send_request(link)
		name:str = get_uploader(response)
		if not name:
			reply = "Errore nel recuperare il nome dell'autore. Riprova."
			await status.edit_text(reply)
			return

		# pagina della submission: immagine in HD e link URI
		html_tag_img = parse_html_tag_image(response)
		if html_tag_img is None:
			reply = "Errore nel recuperare il tag html dell'immagine dall'URL. Riprova."
			await status.edit_text(reply)
			return

		img_tags = get_image_tags(html_tag_img)
		if img_tags is None:
			reply = "Errore nel recuperare i tag dall'immagine. Riprova."
			await status.edit_text(reply)
			return

		await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)

		img_src = get_image_source(html_tag_img)
		if img_src is None:
			await update.message.reply_text("Errore nel recupero della foto.")
			return

		to_spoil, blacklisted_words = check_for_blacklist(img_tags)

		reply:str = (
			f"Autore: {name}\n"
			f"{(blacklisted_words+"\n") if to_spoil else ""}"
			f"Tag: {convert_tags_to_string(img_tags)}\n"
			f"Source: {link}\n"
		)

		await context.bot.send_photo(
			update.message.chat_id,
			photo=img_src,
			has_spoiler=to_spoil,
			caption=reply
		)
		await status.delete()
	except httpx.HTTPStatusError as e:
		await status.edit_text(f"Errore HTTP - codice {e.response.status_code}. Riprova più tardi.")
	except httpx.RequestError:
		await status.edit_text("Impossibile raggiungere furaffinity.net. Verifica che la tua connessione sia attiva o che il sito sia online.")

	# Fine metodo