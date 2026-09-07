from src.python_files.commands.submissions import submissions_command

fatto = {
	"Prendere tutte le submissions"
	"Filtrare le submissions"
	"Ricavare le seguenti info:"
	"- autore"
	"- tag (mostrarne massimo 10!)"
	"- link all'immagine"
	"Impacchettare le info come didascalia della foto"

}

da_fare = {
	"Programmare il messaggio ad orari prestabiliti nel canale"
	"Opzionale: creare gruppo per anteprima di messaggio con pulsanti per conferma o eliminazione."
	"In caso di mancata azione, il messaggio verrà inviato all'ora prestabilita"

}

def test_submission(update, context):

	result = submissions_command(update, context, testing=True)



