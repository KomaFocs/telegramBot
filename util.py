import requests
from bs4 import BeautifulSoup
from requests import Response
from telegram.ext import ContextTypes

SOURCE = 'data-fullview-src'
DATA_TAGS = 'data-tags'
TITLE = 'alt'  # su Furaffinity 'alt' è usato come 'title' per le <img>... idk man
KOMA_URL = "https://www.furaffinity.net/view/66145507"


def connect_to_FA(url:str) -> Response | int:
	with open("cookies/cookies.txt", "r") as file:
		lines = file.readlines()
	COOKIES = {"a": lines[0].strip(), "b": lines[1].strip()}
	response = requests.get(url, cookies=COOKIES)
	return response if response.status_code == 200 else response.status_code

def check_url(context: ContextTypes.DEFAULT_TYPE) -> str:
	return KOMA_URL if len(context.args) == 0 or not "www.furaffinity.net" in context.args[0] else context.args[0]

def parse(response:Response) -> BeautifulSoup | None:
	return BeautifulSoup(response.text, 'html.parser') if response else None

def parse_html_tag_img(response:Response) -> BeautifulSoup | None:
	img = BeautifulSoup(response.text, 'html.parser').find('img', attrs={SOURCE: True})
	return img if img else None

def get_img_title(img:BeautifulSoup) -> str | None:
	return img[TITLE] if img else None

def get_img_tags(img:BeautifulSoup) -> list[str] | None:
	tags = ["#"+tag for tag in img[DATA_TAGS].split(" ") if not (len(tag) >= 2 and tag[0].isalpha() and tag[1] == "_")]
	return tags if img else None

def get_img_tags_as_string(tags:list[str]) -> str:
	return ", ".join(tags)

def get_author(response:Response) -> str | None:
	return parse(response).find("title").getText().split("by")[1].split("--")[0].strip() if response else None

def get_image_source(img:BeautifulSoup) -> str | None:
	if img is None: return None
	return "https:" + img[SOURCE] if img[SOURCE].startswith("//") else img[SOURCE]


def check_for_blacklist(img_tags: list[str]) -> tuple[bool, str]:
	with open("blacklisted_words.txt", "r") as bw:
		words = bw.read().split(" ")
		comuni = list(set(words) & set(img_tags))
		word_found = len(comuni) > 0
		msg = f"La foto contiene almeno un tag nella blacklist: {', '.join(comuni)}." if len(comuni) > 0 else ""
	return word_found, msg

