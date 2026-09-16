from datetime import time
from enum import StrEnum, Enum
from pathlib import Path


MINI_APP_PREFIX:str = "from-mini-app_"
PAROLA:str = "macro"
FA_URL:str = "https://www.furaffinity.net"
USER_URL:str = f"{FA_URL}/user"

HIOSHIRU_FILE:str = "hioshiru_stickers.txt"

STUNNED_STRING:str = "stunned_until"
DEFAULT_STUN_DURATION:int = 60
DELETE_INCOMING_MESSAGES:str = "delete_incoming"

MAX_TAGS_IN_MESSAGE:int = 10
TAG_SEPARATOR:str = " "
JOB_QUEUE:str = "job_queue"
JOB_QUEUE_TASK:str = "job_queue_task"

MAX_BACKUPS:int = 3

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
	CHATS = SECRETS / "chats"

	IMG_FILES = SRC / "img_files"
	TXT_FILES = SRC / "txt_files"
	PYTHON_FILES = SRC / "python_files"
	DATABASE_FILES = SECRETS / "database_files"
	BACKUP_FILES = DATABASE_FILES / "backup_files"

	DATABASE = DATABASE_FILES / "bot.db"

	RESTORE_FILE = DATABASE_FILES / "restore_file.txt"
	COOKIES_FILE = SECRETS / "cookies.txt"
	BLACKLIST_FILE = TXT_FILES / "blacklist.txt"
	WHITELIST_FILE = TXT_FILES / "whitelist.txt"
	TOKEN_FILE = SECRETS / "token.txt"
	SPECIES_FILE = SECRETS / "species.txt"
	PRIORITY_TAGS_FILE = SECRETS / "priority_tags.txt"

	CHANNEL_MACROMICROITALIA = CHATS / "canale_macromicroitalia.txt"
	CHANNEL_TEST = CHATS / "canale_test.txt"
	GROUP_MEGLIOMACRO = CHATS / "gruppo_megliomacro.txt"
	GROUP_TEST = CHATS / "gruppo_test.txt"


class ORARI(Enum):
	MEZZANOTTE = time(0, 0)
	CINQUE = time(5, 0)
	DIECI = time(10, 0)
	QUINDICI = time(15, 0)
	VENTI = time(20, 0)


class STATUS(StrEnum):
	APPROVED = "approved"
	REJECTED = "rejected"
	PENDING = "pending"
	SENT = "sent"


class FILTER(StrEnum):
	IS_ALLOWED = "is_allowed"
	IS_BLACKLISTED = "is_blacklisted"
	IS_WHITELISTED = "is_whitelisted"
	BLACKLIST_MATCHES = "blacklist_matches"
	WHITELIST_MATCHES = "whitelist_matches"


class DATABASE_TABLES:
	IMAGES = "images"
	MESSAGES = "messages"
	USERS = "users"


class DATABASE_TABLE_ID(StrEnum):
	OF_USERS = "username"
	OF_IMAGES = "image_id"
	OF_MESSAGES = "image_id"


class HTML_TAG(StrEnum):
	TITLE = "title"
	HREF = "href"
	SOURCE = "src"
	IMG = "img"
	VIEW = "a[href^=\"/view/\"][title]"
	DATASOURCE = "data-src"
	DATATAGS = "data-tags"
	FIGURE = "figure"
	AUTHOR = "p i + a"
	NEXT_PAGE = "a.button.more"
	HD_IMAGE = "#submissionImg"
