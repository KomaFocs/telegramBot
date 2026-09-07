from pathlib import Path

from src.python_files.models.image import Image
from src.python_files.utils.constants import FILTER, DIR


def get_from_file(file:Path) -> list[str]:
	if file.is_file():
		return [word.lower() for word in file.read_text(encoding="utf-8").split()]
	return []


def _clean_tags(tags:list[str]|set[str]|None) -> set[str]:
	if not tags:
		return set()
	return {tag.lower().removeprefix("#") for tag in tags}


def _define_filters(files:list[Path]) -> tuple[set[str], ...]:
	if not files:
		return set(),set()

	sets = [_clean_tags(get_from_file(f)) for f in files]
	return tuple(sets)


FILES = [DIR.WHITELIST_FILE, DIR.BLACKLIST_FILE]
whitelist_set, blacklist_set = _define_filters(FILES)  # istanziato una volta sola, all'importazione del file .py


def eval_submission_tags(img_tags:list[str]|set[str], whitelist:set[str]=None, blacklist:set[str]=None) -> dict:
	tag_set:set[str] = {t.lower().removeprefix("#") for t in img_tags}
	blacklist_matches:set[str] = tag_set & (blacklist or set())
	whitelist_matches:set[str] = tag_set & (whitelist or set())
	is_blacklisted:bool = bool(blacklist_matches)
	is_whitelisted:bool = bool(whitelist_matches)
	is_allowed:bool = not is_blacklisted and (is_whitelisted if whitelist else True)

	return {
		FILTER.IS_ALLOWED: is_allowed,
		FILTER.IS_BLACKLISTED: is_blacklisted,
		FILTER.IS_WHITELISTED: is_whitelisted,
		FILTER.BLACKLIST_MATCHES: blacklist_matches,
		FILTER.WHITELIST_MATCHES: whitelist_matches
	}


def check_for_blacklist(img_tags: list[str], blacklist:list[str]=None) -> tuple[bool, str]:
	if not img_tags:
		return False, ""

	bl:set = blacklist_set if blacklist is None else _clean_tags(blacklist)
	result:dict = eval_submission_tags(img_tags, blacklist=bl)
	if result[FILTER.IS_BLACKLISTED]:
		matches:str = ", ".join(f"#{tag}" for tag in result[FILTER.BLACKLIST_MATCHES])
		msg:str = f"La foto contiene alcuni tag presenti nella blacklist: {matches}"
		return True, msg

	return False, ""

def check_for_whitelist(img_tags: list[str], whitelist:list[str]=None) -> tuple[bool, str]:
	if not img_tags:
		return False, ""

	wl:set = whitelist_set if whitelist is None else _clean_tags(whitelist)
	result:dict = eval_submission_tags(img_tags, whitelist=wl)
	if result[FILTER.IS_WHITELISTED]:
		return True, ""

	return False, ""


def filter_submissions(images:list[Image], whitelist:list[str]=None, blacklist:list[str]=None) -> list[Image]:
	wl = whitelist_set if whitelist is None else _clean_tags(whitelist)
	bl = blacklist_set if blacklist is None else _clean_tags(blacklist)

	return [
		img for img in images if eval_submission_tags(img.tags, whitelist=wl, blacklist=bl)[FILTER.IS_ALLOWED]
	]


