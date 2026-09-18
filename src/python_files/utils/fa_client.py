import httpx
from httpx import Response

from datetime import datetime

from bs4 import BeautifulSoup, Tag

from src.python_files.models.image import Image
from src.python_files.models.message import Message
from src.python_files.models.submission import Submission
from src.python_files.models.user import User
from src.python_files.utils.constants import DIR, FA_URL, HTML_TAG


def get_cookies() -> dict | None:
	if not DIR.COOKIES_FILE.exists():
		return None
	lines = DIR.COOKIES_FILE.read_text().splitlines()
	return {"a": lines[0].strip(), "b": lines[1].strip()} if len(lines) > 1 else None


async def send_request(url:str) -> Response | None:
	async with httpx.AsyncClient(cookies=get_cookies(), follow_redirects=True) as client:
		try:
			return await client.get(url, timeout=60)
		except Exception:
			print(f"Errore per url = {url}")
			return None


def convert_to_soup(response: Response) -> BeautifulSoup:
	return BeautifulSoup(response.text, "html.parser")


def get_all_submissions(response:Response) -> list[Submission] | None:
	soup:BeautifulSoup = convert_to_soup(response)
	submissions:list[Submission] = []

	for tag in soup.select(HTML_TAG.FIGURE):
		user:User = get_user(tag)
		img:Image = get_image(tag, user.username)
		message:Message = Message(
			image_id = img.image_id
		)

		submissions.append(
			Submission(
				image=img,
				user=user,
				message=message,
			)
		)
	return submissions


def get_user(tag:Tag) -> User | None:
	author:Tag = tag.select_one(HTML_TAG.AUTHOR)
	username:str = author[HTML_TAG.HREF].strip("/").split("/")[-1]
	display_name:str = author[HTML_TAG.TITLE]

	return User(
		username=username,
		display_name=display_name,
	)


def get_tags(tag:Tag) -> str:
	return tag.select_one(HTML_TAG.IMG).get(HTML_TAG.DATATAGS, "")


def get_image(html_tag:Tag, username:str) -> Image | None:
	image:Tag = html_tag.select_one(HTML_TAG.IMG)
	view:Tag = html_tag.select_one(HTML_TAG.VIEW)
	href:str = view.get(HTML_TAG.HREF, "")
	image_id = int(href.split("/")[2])
	source = image[HTML_TAG.SOURCE]
	timestamp = int(source.rsplit("-", 1)[1].split(".",1)[0])

	return Image(
		image_id=image_id,
		username=username,
		title=view[HTML_TAG.TITLE].strip(),
		tags=get_tags(html_tag),
		submission_link=href,
		submission_date=datetime.fromtimestamp(timestamp),
		sd_image_link=f"https:{source}"
	)


def find_next_button(response:Response) -> str | None:
	soup = convert_to_soup(response)
	next_button = soup.select_one(HTML_TAG.NEXT_PAGE)

	if next_button and next_button.get(HTML_TAG.HREF):
		current_url = f"{FA_URL}{next_button.get(HTML_TAG.HREF)}"
	else:
		current_url = None
	return current_url


def parse_hd_image(response: Response) -> str:
	soup = convert_to_soup(response)

	img = soup.select_one(HTML_TAG.HD_IMAGE)
	if not img:
		return ""

	src = img.get(HTML_TAG.SOURCE, "")

	return f"https:{src}" if src.startswith("//") else src


async def prepare_img_to_send(image:Image) -> Image:
	link = image.submission_link
	response = await send_request(link)
	if not response:
		return image

	link = parse_hd_image(response)
	image.hd_image_link = link
	return image
