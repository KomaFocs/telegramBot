import asyncio, random

from telegram.constants import ChatAction
from src.python_files.utils.constants import IMAGE, DIR, BUTTON, FA_URL, ERROR_CHAT_FILE
from src.python_files.utils.decorators import logger, single_execution
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.python_files.utils.filters import get_from_file, filter_submissions
from src.python_files.utils.fa_client import get_images, parse_images, send_request, convert_to_soup, find_next_button
from src.python_files.models.image import Image


@logger
@single_execution()
async def submissions_command(update:Update, context:ContextTypes.DEFAULT_TYPE, testing:bool=False) -> None:
	user_id:str = str(update.effective_user.id)
	allowed_ids:list[str] = get_from_file(DIR.SECRETS/"id.txt")
	if user_id not in allowed_ids:
		msg = "Spiacente, non sei autorizzato a usare questo comando :S"
		await update.message.reply_text(msg)
		return

	current_url = f"{FA_URL}/msg/submissions"
	all_images:list[Image] = []
	size_images:list[Image]
	image:Image

	while current_url:
		response = await send_request(update=update, url=current_url)  # richiedi le foto
		all_images.extend(get_images(response))  # scarica tutte le foto
		current_url = find_next_button(response)  # passa alla pagina successiva

	size_images = filter_submissions(all_images)


	await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
	await asyncio.sleep(2)
	image = random.choice(size_images)

	with open(DIR.SECRETS/ERROR_CHAT_FILE, "r") as file:
		chat_id = file.read().strip().split()[0]

	keyboard = InlineKeyboardMarkup([
		[
			InlineKeyboardButton("✅ Approva", callback_data="approve"),
			InlineKeyboardButton("❌ Rifiuta", callback_data="reject"),
		]
	])

	await context.bot.send_photo(
		chat_id=chat_id,
		photo=image.preview_link,
		caption=image.format_description(),
		reply_markup=keyboard,
	)


