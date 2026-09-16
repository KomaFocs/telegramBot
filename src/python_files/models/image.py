from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.python_files.models.base import Base
from src.python_files.utils.constants import DATABASE_TABLE_ID, DATABASE_TABLES

if TYPE_CHECKING:
	from src.python_files.models.user import User


class Image(Base):
	__tablename__ = DATABASE_TABLES.IMAGES

	image_id:Mapped[int] = mapped_column(
		primary_key=True,
	)

	username:Mapped[str] = mapped_column(
		ForeignKey(f"{DATABASE_TABLES.USERS}.{DATABASE_TABLE_ID.OF_USERS}"),
		nullable=False,
	)

	title:Mapped[str] = mapped_column(
		String,
		nullable=False,
	)

	tags:Mapped[str] = mapped_column(
		Text,
		nullable=False,
	)

	submission_link:Mapped[str] = mapped_column(
		String,
		nullable=False,
	)

	sd_image_link:Mapped[str] = mapped_column(
		String,
		nullable=False,
	)

	hd_image_link: Mapped[str] = mapped_column(
		String,
		nullable=True,
	)

	submission_date:Mapped[datetime] = mapped_column(
		nullable=False,
	)

	users:Mapped["User"] = relationship(
		back_populates=DATABASE_TABLES.IMAGES,
	)