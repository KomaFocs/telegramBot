import io

from bs4 import BeautifulSoup, ResultSet
from src.python_files.utils.decorators import logger, single_execution, chat_action
from telegram import Update
from telegram.ext import ContextTypes
from src.python_files.utils.util import send_request_to_FA, filter_submissions, get_from_file, DIR


@logger
@single_execution()
@chat_action()
async def submissions_command(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	# <a class="notification-container inline" href="/msg/submissions/" title="175 Submission Notifications">175S</a>
	# <a class="button standard more" href="/msg/submissions/new~65089959@72/">Next 72</a> # next page button

	# <img class ="blocked-content" data-tags="u_plinthart c_artwork_digital t_general_furry_art s_hyena beastle male
	# hyena twitch treaming vtuber gif emote sticker cute gaming" alt=""
	# src="//t.furaffinity.net/66232767@300-1788339433.jpg"  data-width="204.211" data-height="200"
	# style="width:204.211px; height:200px" loading="lazy" decoding="async"
	# />

	# <img data-tags="u_plinthart c_artwork_digital t_general_furry_art s_hyena beastle male
	# # hyena twitch treaming vtuber gif emote sticker cute gaming" src="//t.furaffinity.net/66232767@300-1788339433.jpg"
	# />

	FA_URL = "https://www.furaffinity.net"
	SUBMISSIONS_URL = f"{FA_URL}/msg/submissions"

	next_button_link:str|None
	all_images:list = []
	size_images:list[dict]

	current_url = SUBMISSIONS_URL
	while current_url:

		response:BeautifulSoup = await send_request_to_FA(current_url)
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
			raw_src = single_img.get("src") or single_img.get("data-src", "")
			if not raw_src:
				continue

			img_id = raw_src.split("@")[0].split("/")[-1]
			risultato.append({
				"tags": single_img.get("data-tags", "").split(),
				"src": f"{SRC_LINK}/{img_id}",
			})

		all_images.extend(risultato)  # all_images -> tutte le immagini

		next_button = response.select_one("a.button.more")
		if next_button and next_button.get("href"):
			current_url = f"{FA_URL}{next_button.get('href')}"
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

	content: str = "\n".join(f"{index}: {img['src']}" for index, img in enumerate(size_images, start=1))
	file_bytes = io.BytesIO(content.encode("utf-8"))

	await context.bot.send_document(
		chat_id=update.effective_chat.id,
		document=file_bytes,
		filename="immagini_macro.txt",
		caption=f"File contenente i link alle ({len(size_images)}) immagini macro nelle submission di MacroMicroItalia."
	)


