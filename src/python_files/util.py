import requests
from bs4 import BeautifulSoup
from telegram.ext import ContextTypes

SOURCE = 'data-fullview-src'
DATA_TAGS = 'data-tags'
TITLE = 'alt'  # su Furaffinity 'alt' è usato come 'title' per le <img>... idk man

def get_cookies(cookies:list[str] = None):
	with open("../../secrets/cookies.txt", "r") as file:
		lines = file.readlines()
	return lines

# context.args
# args[0] = url

def send_request_to_FA(url:str) -> BeautifulSoup | int:
	cookies = get_cookies()
	COOKIES = {"a": cookies[0].strip(), "b": cookies[1].strip()}
	response = requests.get(url, cookies=COOKIES)
	return BeautifulSoup(response.text, 'html.parser') if response.status_code == 200 else response.status_code

def check_url(context: ContextTypes.DEFAULT_TYPE) -> str | None:
	return None if not context.args or not "furaffinity.net" in context.args[0] else context.args[0]

def check_nsfw(context: ContextTypes.DEFAULT_TYPE) -> bool:
	return context.args[3].lower() == "nsfw" if len(context.args) > 3 else False

def parse_html_tag_img(response:BeautifulSoup) -> BeautifulSoup | None:
	img = response.find('img', attrs={SOURCE: True})
	return img if img else None

def get_img_title(img:BeautifulSoup) -> str | None:
	return img[TITLE] if img else None

def get_img_tags(img:BeautifulSoup) -> list[str] | None:
	tags = ["#"+tag for tag in img[DATA_TAGS].split(" ") if not (len(tag) >= 2 and tag[0].isalpha() and tag[1] == "_")]
	return tags if img else None

def get_img_tags_as_string(tags:list[str]) -> str:
	return ", ".join(tags)

def get_author(response:BeautifulSoup) -> str | None:
	return response.find("title").getText().split("by")[1].split("--")[0].strip() if response else None

def get_image_source(img:BeautifulSoup) -> str | None:
	if img is None: return None
	return "https:" + img[SOURCE] if img[SOURCE].startswith("//") else img[SOURCE]


def check_for_blacklist(img_tags: list[str]) -> tuple[bool, str]:
	with open("../txt_files/blacklisted_words.txt", "r") as bw:
		words = ["#" + s for s in bw.read().split()]
		comuni = list(set(words) & set(img_tags))
		word_found = len(comuni) > 0
		msg = f"La foto contiene almeno un tag nella blacklist: {', '.join(comuni)}." if word_found else ""
		print(words, word_found, comuni)
	return word_found, msg

