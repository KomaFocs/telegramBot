import io
from bs4 import BeautifulSoup, ResultSet
from telegram.constants import ChatAction

from src.python_files.utils.constants import IMAGE, BUTTON, DIR
from src.python_files.utils.decorators import logger, single_execution
from telegram import Update
from telegram.ext import ContextTypes
from src.python_files.utils.filters import get_from_file, filter_submissions
from src.python_files.utils.fa_client import send_request


@logger
@single_execution()
async def submissions_command(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	user_id:str = str(update.effective_user.id)
	allowed_ids:list[str] = get_from_file(DIR.SECRETS/"id.txt")
	if user_id not in allowed_ids:
		msg = "Spiacente, non sei autorizzato a usare questo comando :S"
		await update.message.reply_text(msg)
		return

	FA_URL = "https://www.furaffinity.net"
	SUBMISSIONS_URL = f"{FA_URL}/msg/submissions"

	next_button_link:str|None
	all_images:list = []
	size_images:list[dict]

	current_url = SUBMISSIONS_URL
	while current_url:

		response:BeautifulSoup = await send_request(current_url)
		if isinstance(response, int):
			msg = f"⚠️ Errore {response} durante il recupero da FA su {current_url}"
			await update.message.reply_text(msg)
			return

		lista_img:ResultSet = response.select("b img")
		if not lista_img:
			msg = "Nessuna immagine trovata."
			await update.message.reply_text(msg)
			return

		SRC_LINK:str = f"{FA_URL}/view"
		risultato:list = []

		for single_img in lista_img:
			raw_src = single_img.get(IMAGE.SOURCE) or single_img.get(IMAGE.DATASOURCE, "")
			if not raw_src:
				continue

			img_id = raw_src.split("@")[0].split("/")[-1]
			risultato.append({
				IMAGE.TAGS: single_img.get(IMAGE.DATATAGS, "").split(),
				IMAGE.SOURCE: f"{SRC_LINK}/{img_id}",
			})

		all_images.extend(risultato)  # all_images -> tutte le immagini

		next_button = response.select_one("a.button.more")
		if next_button and next_button.get(BUTTON.HREF):
			current_url = f"{FA_URL}{next_button.get(BUTTON.HREF)}"
		else:
			current_url = None

	if not all_images:
		msg = "Nessuna immagine estratta dalla pagina delle submissions."
		await update.message.reply_text(msg)
		return


	whitelist = get_from_file(DIR.WHITELIST_FILE)
	blacklist = get_from_file(DIR.BLACKLIST_FILE)
	size_images = filter_submissions(all_images, whitelist, blacklist)  # ora solo immagini size

	if not size_images:
		msg = "Nessuna immagine corrisponde ai criteri di filtraggio."
		await update.message.reply_text(msg)
		return

	await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_DOCUMENT)
	content: str = "\n".join(f"{index}: {img[IMAGE.SOURCE]}" for index, img in enumerate(size_images, start=1))
	file_bytes = io.BytesIO(content.encode("utf-8"))

	await context.bot.send_document(
		chat_id=update.effective_chat.id,
		document=file_bytes,
		filename="immagini_macro.txt",
		caption=f"File contenente i link alle ({len(size_images)}) immagini size nelle submission di MacroMicroItalia."
	)


