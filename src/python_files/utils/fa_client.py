import httpx
from bs4 import BeautifulSoup, Tag
from httpx import Response
from telegram import Update
from src.python_files.models.image import Image
from src.python_files.utils.constants import DIR, IMAGE, FA_URL, BUTTON


def get_cookies() -> dict | None:
	if not DIR.COOKIES_FILE.exists():
		return None
	lines = DIR.COOKIES_FILE.read_text().splitlines()
	return {"a": lines[0].strip(), "b": lines[1].strip()} if len(lines) > 1 else None


async def send_request(update:Update, url:str) -> Response | None:
	async with httpx.AsyncClient(cookies=get_cookies(), follow_redirects=True) as client:
		try:
			return await client.get(url, timeout=60)
		except Exception:
			error_message: str = f"⚠️ Errore durante il collegamento a {url}"
			await update.message.reply_text(error_message)
			return None


def convert_to_soup(response: Response) -> BeautifulSoup:
	return BeautifulSoup(response.content, "html.parser")


def parse_images(response:Response) -> list[Image]:
	images = []
	soup = convert_to_soup(response)
	for figure in soup.select("figure"):
		img: Tag = figure.select_one("img")
		author: Tag = figure.select_one("p i + a")
		link: Tag = figure.select_one("figcaption p a")
		href = link.get(IMAGE.HREF, "") if link else ""
		submission_id:int = int((href.split("/")[2]) if link else 0)

		image = Image(
			author = author.get(IMAGE.TITLE, "") if author else "",
			_tags = img.get(IMAGE.DATATAGS, "").split() if img else [],
			submission_link = FA_URL + (link.get(IMAGE.HREF, "") if link else ""),
			preview_link = f"https:{img.get(IMAGE.SOURCE, "")}" if img else "",
			submission_id = submission_id,
		)
		images.append(image)
	return images


def get_images(response:Response) -> list[Image] | None:
	return parse_images(response)


def find_next_button(response:Response) -> str | None:
	soup = convert_to_soup(response)
	next_button = soup.select_one(BUTTON.NEXT_PAGE)

	if next_button and next_button.get(BUTTON.HREF):
		current_url = f"{FA_URL}{next_button.get(BUTTON.HREF)}"
	else:
		current_url = None
	return current_url

