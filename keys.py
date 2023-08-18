from telebot.types import ReplyKeyboardMarkup, KeyboardButton


class Keyboard:
	def __init__(self, keys_data):
		"""
		data:
		[
			[text, text],
			[text, text],
			[text]
		]
		"""
		self.keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
		for line in keys_data:
			self.keyboard.row(
				*(KeyboardButton(text=x) for x in line)
			)
