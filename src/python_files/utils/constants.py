from datetime import time
from enum import StrEnum
from pathlib import Path


SOURCE:str = "data-fullview-src"
DATA_TAGS:str = "data-tags"
TITLE:str = "alt"

PAROLA:str = "macro"
FA_URL:str = "https://www.furaffinity.net"
MINI_APP_PREFIX:str = "from-mini-app_"
DEFAULT_STUN_DURATION:int = 60
HIOSHIRU_FILE:str = "hioshiru_stickers.txt"
STUNNED_STRING:str = "stunned_until"
ERROR_CHAT_FILE:str = "error_chat.txt"
DELETE_INCOMING_MESSAGES:str = "delete_incoming"
CHATS_FILE:str = "chats.txt"
ORARI:list[time] = [
	time(5,0),
	time(10,0),
	time(15,0),
	time(20,0),
	time(0,0),
]

class DIR:
	@staticmethod
	def _get_root() -> Path:
		current:Path = Path(__file__).resolve()
		for parent in current.parents:
			if (parent / "src").is_dir():
				return parent
		return current.parent

	ROOT = _get_root()  # root del progetto
	SRC = ROOT / "src"
	SECRETS = ROOT / "secrets"

	IMG_FILES = SRC / "img_files"
	TXT_FILES = SRC / "txt_files"
	PYTHON_FILES = SRC / "python_files"

	COOKIES_FILE = SECRETS / "cookies.txt"
	BLACKLIST_FILE = TXT_FILES / "blacklist.txt"
	WHITELIST_FILE = TXT_FILES / "whitelist.txt"
	TOKEN_FILE = SECRETS / "token.txt"


class FILTER(StrEnum):
	IS_ALLOWED = "is_allowed"
	IS_BLACKLISTED = "is_blacklisted"
	IS_WHITELISTED = "is_whitelisted"
	BLACKLIST_MATCHES = "blacklist_matches"
	WHITELIST_MATCHES = "whitelist_matches"

class IMAGE(StrEnum):
	TAGS = "tags"
	SOURCE = "src"
	DATASOURCE = "data-src"
	DATATAGS = "data-tags"
	HREF = "href"
	TITLE = "title"

class BUTTON(StrEnum):
	HREF = "href"
	NEXT_PAGE = "a.button.more"