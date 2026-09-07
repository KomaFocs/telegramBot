from dataclasses import dataclass
from datetime import datetime, timedelta

from src.python_files.utils.constants import ORARI

@dataclass
class MessaggioProgrammato:
	id:int
	didascalia:str
	data:datetime

	def schedule(self, ultimo_invio:datetime):
		data = ultimo_invio.date()

		for orario in ORARI:
			prossimo = datetime.combine(data, orario)

			if prossimo > ultimo_invio:
				return prossimo

		# se non ha trovato il prossimo, allora bisogna andare avanti di un giorno
		return datetime.combine(data + timedelta(days=1), ORARI[0])