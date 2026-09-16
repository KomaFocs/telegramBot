from telegram import (
	Update,
	CallbackQuery,
)
from telegram.ext import ContextTypes

from src.python_files.utils.constants import STATUS


async def handle_callback(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	query: CallbackQuery = update.callback_query

	action, sub_id = query.data.split(":", 1)
	match action:
		case STATUS.APPROVED:
			await update.effective_chat.send_message(f"{STATUS.APPROVED}!")
			await query.answer(f"Status aggiornato nel database a: {STATUS.APPROVED}")
			# approve_submission(int(sub_id))

		case STATUS.REJECTED:
			await update.effective_chat.send_message(f"{STATUS.REJECTED}!")
			await query.answer(f"Status aggiornato nel database a: {STATUS.REJECTED}")
			# reject_submission(int(sub_id))

		case _:
			pass
			# raise CallbackException(
			#     update=update,
			#     message=f"Valore callback_query '{action}' non ammesso",
			# )

