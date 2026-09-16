import asyncio
import random

import httpx
from telegram import Message, Update
from telegram.constants import ChatAction
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from src.python_files.config.lista_tipi import FA_Type
from src.python_files.models.image import Image
from src.python_files.models.submission import Submission
from src.python_files.utils.constants import FA_URL
from src.python_files.utils.decorators import chat_action,logger,single_execution
from src.python_files.utils.fa_client import get_all_submissions, send_request
from src.python_files.utils.filters import check_for_blacklist,filter_submissions
from src.python_files.utils.telegram_helpers import check_url


@logger
@single_execution()
@chat_action()
async def furaffinity_command(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	msgs: list[str] = [
		"Ci sto lavorando",
		"Un attimo",
		"Richiesta ricevuta",
		"🤔",
		"Agli ordini, capo 🫡"
	]

	status: Message = await update.message.reply_text(
		f"{random.choice(msgs)}..."
	)

	categoria: str = FA_Type.ARTE.value
	query: str = "macro"

	link: str = (
		f"{FA_URL}/search/"
		f"?q={query}&mode=extended&type-{categoria}=1"
	)

	try:
		if context.args:
			link = check_url(context)

			if not link:
				await status.edit_text("Link non valido: devi fornire un link di furaffinity.")
				return

		response = await send_request(url=link)

		if response is None:
			await status.edit_text("Errore nel ricevere info dal server.")
			return

		submissions:list[Submission] = get_all_submissions(response)
		filtered:list[Image] = filter_submissions(submissions)

		if not filtered:
			await status.edit_text("Non ho trovato immagini valide.")
			return

		first_submission:Image = filtered[0]

		to_spoil, spoil_msg = check_for_blacklist(first_submission.tags)

		full_text: str = (
			f"{first_submission.tags}\n{spoil_msg}"
		)

		chat_id = update.effective_chat.id

		await context.bot.send_chat_action(
			chat_id=chat_id,
			action=ChatAction.UPLOAD_PHOTO,
		)

		await asyncio.sleep(
			random.uniform(1, 3)
		)

		await context.bot.send_photo(
			chat_id=chat_id,
			photo=first_submission.sd_image_link,
			has_spoiler=to_spoil,
			caption=full_text,
		)

		await status.delete()

	except httpx.HTTPStatusError as e:
		await status.edit_text(
			f"Errore HTTP - codice {e.response.status_code}. "
			"Riprova più tardi."
		)

	except httpx.RequestError:
		await status.edit_text(
			"Impossibile raggiungere furaffinity.net. "
			"Verifica che la tua connessione sia attiva "
			"o che il sito sia online."
		)

	except TelegramError as e:
		await status.edit_text(
			f"È successo questo: {e.message}."
		)