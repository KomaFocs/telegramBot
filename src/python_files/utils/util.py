from urllib.parse import urlparse

import httpx
from pathlib import Path
from bs4 import BeautifulSoup
from telegram.ext import ContextTypes

class DIR:
	@staticmethod
	def _get_root() -> Path:
		current = Path(__file__).resolve()
		for parent in current.parents:
			if (parent / "src").is_dir():
				return parent
		return current.parent

	ROOT = _get_root()  # root del progetto
	SRC = ROOT / "src"
	SECRETS = ROOT / "secrets"

	IMG = SRC / "img_files"
	TXT = SRC / "txt_files"
	PYTHON = SRC / "python_files"

	COOKIES_FILE = SECRETS / "cookies.txt"
	BLACKLIST_FILE = TXT / "blacklisted_words.txt"
	TOKEN_FILE = SECRETS / "token.txt"

SOURCE = 'data-fullview-src'
DATA_TAGS = 'data-tags'
TITLE = 'alt'  # su Furaffinity 'alt' è usato come 'title' per le <img>... idk man
PAROLA = "macro"


def get_cookies() -> dict | None:
	if not DIR.COOKIES_FILE.exists():
		return None
	lines = DIR.COOKIES_FILE.read_text().splitlines()
	return {"a": lines[0].strip(), "b": lines[1].strip()} if len(lines) > 1 else None


async def send_request_to_FA(url:str) -> BeautifulSoup | int:
	async with httpx.AsyncClient(cookies=get_cookies(), follow_redirects=True) as client:
		try:
			response = await client.get(url, timeout=10)
			return BeautifulSoup(response.text, "html.parser") if response.status_code == 200 else response.status_code
		except httpx.RequestError:
			return -1


def check_url(context: ContextTypes.DEFAULT_TYPE) -> str | None:
	if not context.args: return None

	VALID_HOSTNAME = "furaffinity.net"
	raw_url = next((arg for arg in context.args if VALID_HOSTNAME in arg.lower()), None)
	if not raw_url: return None

	url_to_parse = raw_url if raw_url.lower().startswith("http://", "https://") else f"https://{raw_url}"
	parsed = urlparse(url_to_parse)
	hostname = parsed.hostname.lower() if parsed.hostname else ""
	if hostname == VALID_HOSTNAME or hostname.endswith(VALID_HOSTNAME):
		return parsed._replace(scheme="https").geturl()

	return None


def check_nsfw(context: ContextTypes.DEFAULT_TYPE) -> bool:
	return context.args[3].lower() == "nsfw" if len(context.args) > 3 else False

def parse_html_tag_img(response:BeautifulSoup) -> BeautifulSoup | None:
	img = response.find('img', attrs={SOURCE: True})
	return img if img else None

def get_img_title(img:BeautifulSoup) -> str | None:
	return img[TITLE] if img else None

def get_img_tags(img:BeautifulSoup) -> list[str] | None:
	if not img or DATA_TAGS not in img.attrs:
		return None
	tags:list = []
	for tag in img[DATA_TAGS].split(" "):
		if not (len(tag) >= 2 and tag[0].isalpha() and tag[1] == "_"):
			clean_tag = tag.replace("-", "_")
			tags.append(f"#{clean_tag}")
	return tags

def get_img_tags_as_string(tags:list[str]) -> str:
	return ", ".join(tags)

def get_author(response:BeautifulSoup) -> str | None:
	return response.find("title").getText().split("by")[1].split("--")[0].strip() if response else None

def get_img_source(img:BeautifulSoup) -> str | None:
	if img is None: return None
	return "https:" + img[SOURCE] if img[SOURCE].startswith("//") else img[SOURCE]


def check_for_blacklist(img_tags: list[str]) -> tuple[bool, str]:
	no_match_found = (False, "")
	if not DIR.BLACKLIST_FILE.exists():
		return no_match_found

	words = {"#" + word.lower() for word in DIR.BLACKLIST_FILE.read_text().split()}
	match = words.intersection(set(img_tags))
	blacklisted_words_found = f"Attenzione: la foto contiene almeno un tag nella blacklist: {', '.join(match)}."

	return (True, blacklisted_words_found) if match else no_match_found


