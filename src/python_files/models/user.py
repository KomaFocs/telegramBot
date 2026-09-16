from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.python_files.models.base import Base
from src.python_files.utils.constants import DATABASE_TABLES, USER_URL

if TYPE_CHECKING:
    from src.python_files.models.image import Image


class User(Base):
    __tablename__ = DATABASE_TABLES.USERS

    username: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    display_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    images:Mapped[list["Image"]] = relationship(
        back_populates=DATABASE_TABLES.USERS,
    )

    @property
    def link(self) -> str:
        return f"{USER_URL}/{self.username}"

    def __str__(self) -> str:
        return self.display_name