from enum import Enum

from src.python_files.commands.furaffinity import furaffinity_command
from src.python_files.commands.submissions import submissions_command
from src.python_files.commands.simple_commands.img import img_command
from src.python_files.commands.simple_commands.meglio import meglio_command
from src.python_files.commands.simple_commands.start import start_command
from src.python_files.commands.simple_commands.guida import guida_command

class Nome_Comandi(str, Enum):
	START = "start"
	MEGLIO = "meglio"
	IMG = "img"
	FURAFFINITY = "furaffinity"
	SUBMISSIONS = "submissions"
	GUIDA = "guida"

	def __str__(self) -> str:
		return self.value

COMANDI = {

	Nome_Comandi.START.value: (start_command, "🏃🏽‍➡️ Avvia il bot"),
	Nome_Comandi.MEGLIO.value: (meglio_command, "🗣️ Ti dico cos'è meglio"),
	Nome_Comandi.IMG.value: (img_command, "🗾 Ti invio un'immagine"),
	Nome_Comandi.FURAFFINITY.value: (furaffinity_command, "🎨 Ti invio una foto da Furaffinity."),
	Nome_Comandi.SUBMISSIONS.value: (submissions_command, "🚫 Riservato a Piano e Koma. Per favore non usarlo."),
	Nome_Comandi.GUIDA.value: (guida_command, "📜 Ti spiego in dettaglio le funzioni.")

}
