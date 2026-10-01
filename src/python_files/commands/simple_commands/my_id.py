from telegram import Update, User as TelegramUser, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ChatType, ParseMode
from telegram.ext import ContextTypes

from src.python_files.utils.telegram_helpers import rendi_grassetto


async def my_id(update:Update, context:ContextTypes.DEFAULT_TYPE) -> str|None:
	response:str = ""

	if update.effective_chat.type != ChatType.CHANNEL:
		user:TelegramUser = update.effective_user
		response = (
			f"Telegram ID: {rendi_grassetto(str(user.id))}\n"
			f"Nome completo: {rendi_grassetto(user.full_name)}\n"
			f"Soprannome: {rendi_grassetto(user.username)}\n"
			f"Premium: {rendi_grassetto(str(user.is_premium))}\n"
		)
		keyboard:InlineKeyboardMarkup = InlineKeyboardMarkup([
			[
				InlineKeyboardButton(
					text="Contatta",
					url=user.link
				)
			]
		])

		await update.effective_chat.send_message(
			text=response,
			parse_mode=ParseMode.MARKDOWN_V2,
			reply_markup=keyboard
		)

	return response if response != "" else None
