import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from src.python_files.models.base import Base
from src.python_files.utils.constants import DIR, MAX_BACKUPS

DIR.DATABASE_FILES.mkdir(parents=True, exist_ok=True)
engine:Engine = create_engine(f"sqlite:///{DIR.DATABASE}")
SessionLocal:sessionmaker = sessionmaker(bind=engine,expire_on_commit=False)


def init_db() -> None:
	Base.metadata.create_all(engine)


def get_session() -> Session:
	return SessionLocal()


def backup_database(database_path:Path, backup_dir:Path) -> None:
	backup_dir.mkdir(parents=True, exist_ok=True)
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

	backups_path:Path = backup_dir / f"backup_{timestamp}.db"

	with sqlite3.connect(database_path) as source:
		with sqlite3.connect(backups_path) as destination:
			source.backup(destination)

	backups = sorted(
		backup_dir.glob("backup_*.db"),
		key=lambda path: path.stat().st_mtime,
		reverse=True
	)
	for old_backup in backups[MAX_BACKUPS:]:
		old_backup.unlink()


def restore_database(backup_path:Path, database_path:Path) -> None:
	if not backup_path.exists():
		raise FileNotFoundError(f"Backup non trovato: {backup_path}")

	shutil.copy2(
		src=backup_path,
		dst=database_path,
	)