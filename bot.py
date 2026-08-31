import datetime, io, random
from enum import Enum
from telegram import Update, Message, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from util import *

BOT_TOKEN = open("secrets/token.txt", "r").read()
BOT_USERNAME = "@NeedForBot"

oggi:datetime.date
parola:str

def interceptor(function):
	def wrapper(*args, **kwargs):
		cmd:str = function.__name__.split("_")[0]
		update:Update = args[0]
		first_name:str = update.message.from_user.first_name
		now = datetime.datetime.now()
		data = now.strftime("%d/%m/%Y")
		orario = now.strftime("%H:%M:%S")
		print(f"[{data} {orario}] {first_name} used the {cmd} command.")
		return function(*args, **kwargs)
	return wrapper

class MessageType(Enum):
	GROUP = "group"
	PRIVATE = "private"

def def_parola() -> datetime.date:
	global oggi, parola
	oggi = datetime.date.today()
	parola = "marco" if oggi.day == 1 and oggi.month == 4 else "macro"
	return oggi

@interceptor
async def start_command(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	reply: str = f"Benvenuto. Io sono il bot che ritiene che {parola} sia meglio."
	await update.message.reply_text(reply)

@interceptor
async def meglio_command(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	await update.message.reply_text(f"{parola}.")

@interceptor
async def img_command(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	img = "rick_astley.jpg"
	with open("lyrics.txt", "r") as file:
		lines = file.readlines()
		text = random.choice(lines)

	await update.message.reply_photo(photo=img, caption=text)

@interceptor
async def furaffinity_command(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	URL = check_url(context)
	response = connect_to_FA(URL)
	if isinstance(response, int):  # se è int, allora lo status code non è 200.
		reply = f"Errore con la connessione al sito: Status Code {response}.\nRiprova fra qualche minuto; se hai già riprovato e ancora non funziona, inoltra il messaggio a @KomaFocs."
		await update.message.reply_text(reply)
		return

	# qui invece abbiamo response come tipo Response, da parsare a BeautifulSoup
	html_tag_img = parse_html_tag_img(response)  # parsa, trova e restituisce il tag <img>
	if html_tag_img is None:  # per qualche motivo, non riesce a trovare l'immagine
		reply = "Errore nel recuperare l'immagine dall'URL. Riprova."
		await update.message.reply_text(reply)
		return

	# se invece l'immagine è stata trovata, recuperiamo i tag
	img_tags = get_img_tags(html_tag_img)
	if img_tags is None:
		reply = "Errore nel recuperare i tag dall'URL. Riprova."
		await update.message.reply_text(reply)
		return

	img_src = get_image_source(html_tag_img)
	resp = requests.get(img_src)
	resp.raise_for_status()

	foto = io.BytesIO(resp.content)
	to_spoil = check_for_blacklist(img_tags)[0]
	blacklisted_words = check_for_blacklist(img_tags)[1]

	reply = ""
	reply += f"Autore: {get_author(response)}\n"
	reply += f"Tag: {get_img_tags_as_string(img_tags)}\n"
	reply += f"{blacklisted_words}\n" if to_spoil else ""
	reply += f"Source: {URL}\n"

	await context.bot.send_photo(
		update.message.chat_id,
		photo = foto,
		has_spoiler = to_spoil,
		caption = reply
	)



def handle_response(text: str) -> str | None:
	def_parola()
	message = text.lower()
	meglio_macro = "Sì ok, micro... ma Meglio Macro."
	risposte = ["bravo", "ottimo", "eccellente", "spettacolare", "giusto", "ben detto", "decisamente valido", "basato"]
	if parola in message:
		return random.choice(risposte)
	elif "micro" in message:
		return meglio_macro
	else:
		return f"ERRORE. NON C'È \"{parola.upper()}\" NEL MESSAGGIO."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	message: Message = update.message
	msg_type: str = message.chat.type
	message_string: str = message.text.lower()
	user_id: int = message.from_user.id
	name: str = message.from_user.first_name

	print(f"[{name} ({user_id})] \"{message_string}\"")
	response: str|None = ""

	if msg_type == MessageType.GROUP:
		if BOT_USERNAME.lower() in message_string: # risponde soltanto quando interpellato
			response = handle_response(message_string)
	else:
		response = handle_response(message_string)

	if response is None:
		return

	print(f"[Bot] \"{response}\"")
	await message.reply_text(text=response,reply_to_message_id=message.message_id)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	print(f"\nERROR\nUpdate {update} caused error {context.error}")

async def post_init(app: Application):
	await app.bot.set_my_commands([
		BotCommand("start", "Avvia il bot"),
		BotCommand("meglio", "Ti dico cos'è meglio"),
		BotCommand("img", "Ti mando un'immagine"),
		BotCommand("furaffinity", "Ti mando una foto da FurAffinity"),
    ])


if __name__ == "__main__":
	oggi: datetime.date = def_parola()
	print(f"Starting Bot...\nToday is {oggi.day}/{oggi.month}/{oggi.year}\n")

	app = (
		Application.builder()
		.token(BOT_TOKEN)
		.post_init(post_init)
		.build()
	)

	# Commands
	app.add_handler(CommandHandler("start", start_command))
	app.add_handler(CommandHandler("meglio", meglio_command))
	app.add_handler(CommandHandler("img", img_command))
	app.add_handler(CommandHandler("furaffinity", furaffinity_command))

	# Messages
	app.add_handler(MessageHandler(filters.TEXT, handle_message))

	# Error
	app.add_error_handler(error)

	# Check for messages every <tot> seconds
	print("Checking for new messages...")
	app.run_polling(poll_interval=2)


