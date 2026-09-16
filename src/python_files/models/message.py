from datetime import datetime

from sqlalchemy import ForeignKey, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.python_files.models.base import Base
from src.python_files.models.image import Image
from src.python_files.utils.constants import DATABASE_TABLES, DATABASE_TABLE_ID, STATUS


class Message(Base):
	__tablename__ = DATABASE_TABLES.MESSAGES

	image_id: Mapped[int] = mapped_column(
		ForeignKey(f"{DATABASE_TABLES.IMAGES}.{DATABASE_TABLE_ID.OF_IMAGES}"),
		primary_key=True,
	)
	scheduled_at: Mapped[datetime | None] = mapped_column(
		nullable=True,
	)
	username: Mapped[str] = mapped_column(
		ForeignKey(f"{DATABASE_TABLES.USERS}.{DATABASE_TABLE_ID.OF_USERS}"),
		nullable=False,
	)
	sent_in_group: Mapped[bool] = mapped_column(
		Boolean,
		default=False,
		nullable=False,
	)
	channel_message_id: Mapped[int | None] = mapped_column(
		nullable=True,
	)
	status: Mapped[STATUS] = mapped_column(
		Enum(STATUS),
		nullable=False,
		default=STATUS.PENDING,
	)

	image: Mapped[Image] = relationship()