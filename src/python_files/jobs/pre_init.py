from pathlib import Path

from src.python_files.config.database import restore_database
from src.python_files.utils.constants import DIR


def pre_init() -> None:
	restore_file:Path = DIR.RESTORE_FILE

	if not restore_file.exists():
		return

	backup_name:str = restore_file.read_text().strip()

	if not backup_name:
		return

	restore_database (
		backup_path=DIR.BACKUP_FILES / backup_name,
		database_path=DIR.DATABASE,
	)

	restore_file.unlink()