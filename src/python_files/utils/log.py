from datetime import datetime

from src.python_files.utils.telegram_helpers import beautify_date


def time_log(message:str, timestamp:str=None, show_seconds:bool=False) -> None:
	try:
		if not timestamp:
			timestamp:str = beautify_date(date=datetime.now(), show_seconds=show_seconds)
		print(f"[{timestamp}]: {message}")

	except Exception as e:
		print(f"time_log error: {e}")