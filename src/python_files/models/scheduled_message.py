from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.python_files.models.base import Base
from src.python_files.models.image import Image
from src.python_files.utils.constants import ORARI, STATUS


class MessaggioProgrammato(Base):
	__tablename__ = "scheduled_messages"

	submission_id: Mapped[int] = mapped_column(
		ForeignKey("submissions.submission_id"),
		primary_key=True,
	)

	control_message_id: Mapped[int | None]
	channel_message_id: Mapped[int | None]
	scheduled_at: Mapped[datetime | None]
	status: Mapped[str]
	job_name: Mapped[str | None]

	image: Mapped[Image] = relationship()

	def schedule(self, ultimo_invio: datetime | None = None) -> datetime:
		riferimento = ultimo_invio or datetime.now()
		data = riferimento.date()

		for orario in ORARI:
			prossimo = datetime.combine(data, orario.value)

			if prossimo > riferimento:
				self.scheduled_at = prossimo
				return self.scheduled_at

		self.scheduled_at = datetime.combine(data + timedelta(days=1), ORARI.MEZZANOTTE.value)

		return self.scheduled_at