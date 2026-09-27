from telegram import Update, User as TelegramUser, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ChatType
from telegram.ext import ContextTypes

from src.python_files.utils.telegram_helpers import grassetto


async def my_id(update:Update, context:ContextTypes.DEFAULT_TYPE) -> str|None:
	response:str = ""

	if update.effective_chat.type != ChatType.CHANNEL:
		user:TelegramUser = update.effective_user
		response = (
			f"Telegram ID: {grassetto(str(user.id))}\n"
			f"Nome completo: {grassetto(user.full_name)}\n"
			f"Soprannome: {grassetto(user.username)}\n"
			f"Premium: {grassetto(str(user.is_premium))}\n"
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
			parse_mode="markdown",
			reply_markup=keyboard
		)

	return response if response != "" else None
