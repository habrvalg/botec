import telebot
from keys import Keyboard
from base import *
import os


bot = telebot.TeleBot(token='token')
db = DataBase('public_bot', 'root', 'Ltkmnf-02', 'localhost', 3306)
db.init_tables()
ADMIN_CODE = 'me_admin_UI-02'


@bot.message_handler(commands=['start'])
def start(message):
	id = message.chat.id
	username = message.chat.first_name
	is_admin = db.check_admin(id)

	if username:
		username = f' {username}'
	else:
		username = ''

	if not is_admin:
		bot.send_message(
			message.chat.id,
			f'Здравствуйте{username}, я могу попробовать ответить на ваш вопрос, либо передать его администратору',
			reply_markup=Keyboard([
				['Задать вопрос']
			]).keyboard
		)
	else:
		bot.send_message(
			message.chat.id,
			f'Здравствуйте{username}, я могу попробовать ответить на ваш вопрос, либо передать его администратору',
			reply_markup=Keyboard([
				['Ответить на вопросы'],
				['Задать вопрос'],
				['Добавить администратора', 'Обновить ответы']
			]).keyboard
		)
	db.update_user_mode(id, 'start')


@bot.message_handler(content_types=['text'])
def main(message):

	id = message.chat.id
	text = message.text
	mode = db.get_user_mode(id)
	is_admin = db.check_admin(id)

	username = message.chat.first_name
	is_admin = db.check_admin(id)

	if username:
		username = f' {username}'
	else:
		username = ''

	if mode == 'start':

		if not is_admin:
			if text == 'Задать вопрос':
				bot.send_message(
					id,
					text='Наш бот умеет отвечать как на типовые вопросы, так и на уникальные.\nКакой вопрос вы хотите задать?',
					reply_markup=Keyboard([
						['Типовой', 'Свой вопрос'],
						['Назад']
					]).keyboard
				)
				db.update_user_mode(id, 'choice_q_type')

			elif text == ADMIN_CODE:
				db.set_admin(id)

				bot.send_message(id, 'Вы стали администратором!')

				bot.send_message(
					message.chat.id,
					f'Здравствуйте{username}, я могу попробовать ответить на ваш вопрос, либо передать его администратору',
					reply_markup=Keyboard([
						['Ответить на вопросы'],
						['Задать вопрос'],
						['Добавить администратора', 'Обновить ответы']
					]).keyboard
				)
		else:
			if text == 'Задать вопрос':
				bot.send_message(
					id,
					text='Наш бот умеет отвечать как на типовые вопросы, так и на уникальные.\nКакой вопрос вы хотите задать?',
					reply_markup=Keyboard([
						['Типовой', 'Свой вопрос'],
						['Назад']
					]).keyboard
				)
				db.update_user_mode(id, 'choice_q_type')

			elif text == 'Ответить на вопросы':
				q = db.get_current_q(id)

				if q:
					bot.send_message(id, f"Вопрос:\n\n{q['q']}\n", reply_markup=Keyboard([['Назад'], ['Сменить вопрос']]).keyboard)
					db.update_user_mode(id, 'send_answer')
				else:
					q = db.get_q(id)
					if q:
						bot.send_message(id, f"Вопрос:\n\n{q['q']}\n", reply_markup=Keyboard([['Назад'], ['Сменить вопрос']]).keyboard)
						db.update_user_mode(id, 'send_answer')
					else:
						bot.send_message(id, 'Нет вопросов!')

			elif text == 'Добавить администратора':
				bot.send_message(id, 'Данная функция сейчас недоступна!')

			elif text == 'Обновить ответы':
				bot.send_message(id, 'Пришлите мне Excel файл с типовыми вопросами\nформат файла: xlsx', reply_markup=Keyboard([['Назад']]).keyboard)
				db.update_user_mode(id, 'update_answers_file')

	elif mode == 'choice_q_type':
		if text == 'Типовой':

			qs_ = db.get_qs()
			qs = ''
			for i in range(len(qs_)):
				qs = f'{qs}\n{i+1}) {qs_[i]}'

			bot.send_message(
				id,
				f'Выберите вопрос из предложенных:\n{qs}\n\nОтветы на данные вопросы могут меняться!\nПожалуйста, следите за обновлениями.',
				reply_markup=Keyboard([['Назад']]).keyboard
			)
			db.update_user_mode(id, 'choice_standard_q')

		elif text == 'Свой вопрос':
			bot.send_message(id, 'Введите свой вопрос:', reply_markup=Keyboard([['Назад']]).keyboard)
			db.update_user_mode(id, 'input_uniq_q')

		elif text == 'Назад':
			if not is_admin:
				bot.send_message(
					id,
					text='Наш бот умеет отвечать как на типовые вопросы, так и на уникальные.\nКакой вопрос вы хотите задать?',
					reply_markup=Keyboard([
						['Задать вопрос']
					]).keyboard
				)
			else:
				bot.send_message(
					id,
					text='Наш бот умеет отвечать как на типовые вопросы, так и на уникальные.\nКакой вопрос вы хотите задать?',
					reply_markup=Keyboard([
						['Ответить на вопросы'],
						['Задать вопрос'],
						['Добавить администратора', 'Обновить ответы']
					]).keyboard
				)
			db.update_user_mode(id, 'start')

	elif mode == 'choice_standard_q':
		if text == 'Назад':
			if not is_admin:
				bot.send_message(
					id,
					text='Наш бот умеет отвечать как на типовые вопросы, так и на уникальные.\nКакой вопрос вы хотите задать?',
					reply_markup=Keyboard([
						['Задать вопрос']
					]).keyboard
				)
			else:
				bot.send_message(
					id,
					text='Наш бот умеет отвечать как на типовые вопросы, так и на уникальные.\nКакой вопрос вы хотите задать?',
					reply_markup=Keyboard([
						['Ответить на вопросы'],
						['Задать вопрос'],
						['Добавить администратора', 'Обновить ответы']
					]).keyboard
				)
			db.update_user_mode(id, 'start')

		else:
			try:
				num = int(message.text) - 1
				qs = db.get_qs()
				answers = db.get_answers()

				if (num >= 0) and (num <= len(answers)):
					answer = f'Вопрос:\n{qs[num]}\n\nОтвет:\n{answers[num]}'
					bot.send_message(id, answer)

					qs_ = db.get_qs()
					qs = ''
					for i in range(len(qs_)):
						qs = f'{qs}\n{i + 1}) {qs_[i]}'

					bot.send_message(
						id,
						f'Выберите вопрос из предложенных:\n{qs}\n\nОтветы на данные вопросы могут меняться!\nПожалуйста, следите за обновлениями.',
						reply_markup=Keyboard([['Назад']]).keyboard
					)

				else:
					bot.send_message(id, 'Необходимо ввести номер одного из предложенных ответов!')

			except Exception as e:
				bot.send_message(id, 'Необходимо ввести номер одного из предложенных ответов!')

	elif mode == 'input_uniq_q':
		if text == 'Назад':
			if not is_admin:
				bot.send_message(
					id,
					text='Наш бот умеет отвечать как на типовые вопросы, так и на уникальные.\nКакой вопрос вы хотите задать?',
					reply_markup=Keyboard([
						['Задать вопрос']
					]).keyboard
				)
			else:
				bot.send_message(
					id,
					text='Наш бот умеет отвечать как на типовые вопросы, так и на уникальные.\nКакой вопрос вы хотите задать?',
					reply_markup=Keyboard([
						['Ответить на вопросы'],
						['Задать вопрос'],
						['Добавить администратора', 'Обновить ответы']
					]).keyboard
				)
			db.update_user_mode(id, 'start')

		else:
			db.add_q(id, text)
			if not is_admin:
				bot.send_message(id, 'Ваш вопрос отправлен администратору, скоро вам ответят!', reply_markup=Keyboard([['Задать вопрос']]).keyboard)
			else:
				bot.send_message(id, 'Ваш вопрос отправлен администратору, скоро вам ответят!', reply_markup=Keyboard([
					['Ответить на вопросы'],
					['Задать вопрос'],
					['Добавить администратора', 'Обновить ответы']
				]).keyboard)
			db.update_user_mode(id, 'start')

	elif mode == 'send_answer':
		if text == 'Назад':
			bot.send_message(
				id,
				text='Наш бот умеет отвечать как на типовые вопросы, так и на уникальные.\nКакой вопрос вы хотите задать?',
				reply_markup=Keyboard([
					['Ответить на вопросы'],
					['Задать вопрос'],
					['Добавить администратора', 'Обновить ответы']
				]).keyboard
			)
			db.update_user_mode(id, 'start')

		elif text == 'Сменить вопрос':
			new_q = db.change_q(id)

			if new_q:
				bot.send_message(id, f'Вопрос:\n{new_q}')
			else:
				bot.send_message(id, f'Других вопросов нет!')

		else:
			u_id = db.get_current_user(id)
			q_id = db.get_current_q_id(id)['current_q']

			if u_id:
				u_id = u_id['u_id']
				query = db.get_current_q(id)['q']

				bot.send_message(u_id, f'Получен ответ от администратора!\n\nВаш вопрос:\n{query}\n\nОтвет от администратора:\n{text}')
				db.del_q(q_id)
				bot.send_message(
					id,
					'Ответ отправлен пользователю!',
					reply_markup=Keyboard([
						['Ответить на вопросы'],
						['Задать вопрос'],
						['Добавить администратора', 'Обновить ответы']
					]).keyboard
				)
				db.update_user_mode(id, 'start')

			else:
				bot.send_message(id, 'В боте произошла ошибка, мы не можем отправить ответ пользователю!', reply_markup=Keyboard([
					['Ответить на вопросы'],
					['Задать вопрос'],
					['Добавить администратора', 'Обновить ответы']
				]).keyboard)
				db.update_user_mode(id, 'start')

	elif mode == 'update_answers_file':
		if text == 'Назад':
			bot.send_message(
				id,
				text='Наш бот умеет отвечать как на типовые вопросы, так и на уникальные.\nКакой вопрос вы хотите задать?',
				reply_markup=Keyboard([
					['Ответить на вопросы'],
					['Задать вопрос'],
					['Добавить администратора', 'Обновить ответы']
				]).keyboard
			)
			db.update_user_mode(id, 'start')


@bot.message_handler(content_types=['document'])
def doc_processing(message):
	id = message.chat.id
	mode = db.get_user_mode(id)
	is_admin = db.check_admin(id)

	if is_admin and mode == 'update_answers_file':
		if message.document:

			file_type = message.document.file_name.split('.')[-1]

			if file_type == 'xlsx':
				file_info = bot.get_file(message.document.file_id)
				downloaded_file = bot.download_file(file_info.file_path)

				with open(f'{os.getcwd()}/answers.xlsx', 'wb') as file:
					file.write(downloaded_file)

				db.update_answers()
				bot.send_message(id, 'Файл c ответами обновлён!', reply_markup=Keyboard([
					['Ответить на вопросы'],
					['Задать вопрос'],
					['Добавить администратора', 'Обновить ответы']
				]).keyboard)
				db.update_user_mode(id, 'start')

			else:
				bot.send_message(id, 'Необходим файл с форматом .xlsx')


if __name__ == '__main__':
	bot.infinity_polling()
