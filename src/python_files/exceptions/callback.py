from telegram import Update


class CallbackException(Exception):

	def __init__(self, update:Update, message:str):
		super().__init__(update, message)
		self.update = update
		self.message = message
