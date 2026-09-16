from pathlib import Path

from src.python_files.models.image import Image
from src.python_files.models.submission import Submission
from src.python_files.utils.constants import DIR, FILTER, TAG_SEPARATOR


def get_from_file(file:Path) -> list[str]:
	if not file.is_file():
		return []

	return [ word.lower() for word in file.read_text(encoding="utf-8").split() ]


def _clean_tags(tags:list[str] | set[str] | None) -> set[str]:
	if not tags:
		return set()

	return { tag.lower().removeprefix("#") for tag in tags }


def _define_filters(files:list[Path]) -> tuple[set[str], ...]:
	if not files:
		return set(), set()

	sets = [ _clean_tags(get_from_file(file)) for file in files ]
	return tuple(sets)


FILES = [
	DIR.WHITELIST_FILE,
	DIR.BLACKLIST_FILE,
]

whitelist_set, blacklist_set = _define_filters(FILES)


def eval_submission_tags(img_tags:str, whitelist:set[str] | None = None, blacklist:set[str] | None = None) -> dict:
	tag_set = _clean_tags(img_tags.split(TAG_SEPARATOR))

	blacklist_matches = tag_set & (blacklist or set())
	whitelist_matches = tag_set & (whitelist or set())

	is_blacklisted = bool(blacklist_matches)
	is_whitelisted = bool(whitelist_matches)

	is_allowed = (
		not is_blacklisted
		and (is_whitelisted if whitelist else True)
	)

	return {
		FILTER.IS_ALLOWED: is_allowed,
		FILTER.IS_BLACKLISTED: is_blacklisted,
		FILTER.IS_WHITELISTED: is_whitelisted,
		FILTER.BLACKLIST_MATCHES: blacklist_matches,
		FILTER.WHITELIST_MATCHES: whitelist_matches,
	}


def check_for_blacklist(img_tags:str, blacklist:list[str] | None = None) -> tuple[bool, str]:
	if not img_tags:
		return False, ""

	bl = (
		blacklist_set
		if blacklist is None
		else _clean_tags(blacklist)
	)

	result = eval_submission_tags(img_tags, blacklist=bl)

	if result[FILTER.IS_BLACKLISTED]:
		matches = TAG_SEPARATOR.join(f"#{tag}" for tag in result[FILTER.BLACKLIST_MATCHES])

		return (
			True,
			f"La foto contiene alcuni tag presenti nella blacklist: {matches}",
		)

	return False, ""


def check_for_whitelist(img_tags:str, whitelist:list[str] | None = None) -> tuple[bool, str]:
	if not img_tags:
		return False, ""

	wl = (
		whitelist_set
		if whitelist is None
		else _clean_tags(whitelist)
	)

	result = eval_submission_tags(
		img_tags,
		whitelist=wl,
	)

	return result[FILTER.IS_WHITELISTED], ""


def filter_submissions(images:list[Submission], whitelist:list[str] | None = None, blacklist:list[str] | None = None) -> list[Submission]:
	wl = (
		whitelist_set
		if whitelist is None
		else _clean_tags(whitelist)
	)

	bl = (
		blacklist_set
		if blacklist is None
		else _clean_tags(blacklist)
	)

	return [
		submission
		for submission in images
		if eval_submission_tags(
			submission.image.tags,
			whitelist=wl,
			blacklist=bl,
		)[FILTER.IS_ALLOWED]
	]
