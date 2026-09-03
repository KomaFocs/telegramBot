import random
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from src.python_files.utils.decorators import logger, chat_action
from src.python_files.utils.util import DIR

@logger
@chat_action(ChatAction.UPLOAD_PHOTO)
async def img_command(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	image:str = DIR.IMG/"rick_astley.jpg"
	with open(DIR.TXT/"lyrics.txt", "r") as file:
		lines = file.readlines()
		text = random.choice(lines)
	await update.message.reply_photo(photo=image, caption=text)

