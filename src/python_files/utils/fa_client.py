import httpx
from bs4 import BeautifulSoup
from src.python_files.utils.constants import DIR, SOURCE, DATA_TAGS, TITLE


def get_cookies() -> dict | None:
	if not DIR.COOKIES_FILE.exists():
		return None
	lines = DIR.COOKIES_FILE.read_text().splitlines()
	return {"a": lines[0].strip(), "b": lines[1].strip()} if len(lines) > 1 else None


async def send_request(url:str) -> BeautifulSoup | int:
	async with httpx.AsyncClient(cookies=get_cookies(), follow_redirects=True) as client:
		try:
			response = await client.get(url, timeout=60)
			return BeautifulSoup(response.text, "html.parser") if response.status_code == 200 else response.status_code
		except httpx.RequestError:
			return -1


def parse_html_tag_image(response:BeautifulSoup) -> BeautifulSoup | None:
	img = response.find('img', attrs={SOURCE: True})
	return img if img else None


def get_image_title(img:BeautifulSoup) -> str | None:
	return img[TITLE] if img else None


def get_image_tags(img:BeautifulSoup) -> list[str] | None:
	if not img or DATA_TAGS not in img.attrs:
		return None
	tags:list = []
	for tag in img[DATA_TAGS].split(" "):
		if not (len(tag) >= 2 and tag[0].isalpha() and tag[1] == "_"):
			clean_tag = tag.replace("-", "_")
			tags.append(f"#{clean_tag}")
	return tags


def convert_tags_to_string(tags:list[str]) -> str:
	return ", ".join(tags)


def get_uploader(response:BeautifulSoup) -> str | None:
	return response.find("title").getText().split("by")[1].split("--")[0].strip() if response else None


def get_image_source(img:BeautifulSoup) -> str | None:
	if img is None: return None
	return "https:" + img[SOURCE] if img[SOURCE].startswith("//") else img[SOURCE]


