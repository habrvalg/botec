import pymysql
from pandas import read_excel, DataFrame
from os import getcwd


class DataBase:
	def __init__(self, db_name, user, password, host, port):
		self.db = pymysql.connect(
			database=db_name,
			user=user,
			password=password,
			host=host,
			port=port,
			cursorclass=pymysql.cursors.DictCursor
		)

	def init_tables(self):
		tables = [
			'users(id int primary key, mode varchar(100), is_admin int default 0, current_q int)',
			'uni_q(id int primary key auto_increment, u_id int, q text, sended int default 0)',
			'answers(id int primary key auto_increment, q text not null, a text not null)'
		]
		with self.db.cursor() as cur:
			for table in tables:
				cur.execute(f'CREATE TABLE IF NOT EXISTS {table};')
			self.db.commit()
		print('Настройка базы данных завершена!')

	def update_user_mode(self, user_id, mode):
		with self.db.cursor() as cur:
			cur.execute(f'SELECT id, mode FROM users WHERE id = {user_id};')
			data = cur.fetchall()
		if len(data) == 0:
			with self.db.cursor() as cur:
				cur.execute(f'INSERT INTO users(id, mode) VALUES({user_id}, "{mode}");')
			data = [{'id': user_id, 'mode': mode}]
		else:
			with self.db.cursor() as cur:
				cur.execute(f'UPDATE users SET mode="{mode}" WHERE id={user_id};')
		self.db.commit()
		return data[0]

	def get_user_mode(self, user_id):
		with self.db.cursor() as cur:
			cur.execute(f'SELECT id, mode FROM users WHERE id = {user_id};')
			data = cur.fetchall()
		if len(data) == 0:
			self.update_user_mode(user_id, 'start')
			return 'start'
		return data[0]['mode']

	def check_admin(self, user_id):
		with self.db.cursor() as cur:
			cur.execute(f'SELECT is_admin FROM users WHERE id = {user_id};')
			data = cur.fetchall()
		if len(data) == 0:
			return False
		return {0: False, 1: True}[data[0]['is_admin']]

	def set_admin(self, user_id):
		with self.db.cursor() as cur:
			cur.execute(f'UPDATE users SET is_admin=1 WHERE id={user_id};')
		self.db.commit()

	def add_q(self, u_id, q):
		with self.db.cursor() as cur:
			cur.execute(f'INSERT INTO uni_q(u_id, q) VALUES({u_id}, "{q}");')

	def del_q(self, id):
		with self.db.cursor() as cur:
			cur.execute(f'DELETE FROM uni_q WHERE id={id};')
			cur.execute(f'UPDATE users SET current_q=NULL where current_q={id};')
		self.db.commit()

	def mark_q(self, id, u_id):
		with self.db.cursor() as cur:
			cur.execute(f'UPDATE uni_q SET sended=1 where id={id};')
			cur.execute(f'UPDATE users SET current_q={id} WHERE id={u_id};')
		self.db.commit()

	def get_q(self, u_id):
		with self.db.cursor() as cur:
			cur.execute(f'SELECT id, u_id, q FROM uni_q WHERE sended=0 LIMIT 1;')
		ans = cur.fetchall()

		if len(ans) == 0:
			return {}

		self.mark_q(ans[0]['id'], u_id)
		return ans[0]

	def get_current_q(self, u_id):
		cur_id = None
		with self.db.cursor() as cur:
			cur.execute(f'SELECT current_q FROM users WHERE id={u_id};')
		cur_id = cur.fetchall()[0]['current_q']

		if cur_id:

			with self.db.cursor() as cur:
				cur.execute(f'SELECT q FROM uni_q WHERE id={cur_id};')

			return cur.fetchall()[0]

		else:
			return False

	def get_current_q_id(self, u_id):
		with self.db.cursor() as cur:
			cur.execute(f'SELECT current_q FROM users WHERE id={u_id};')
		return cur.fetchall()[0]

	def get_current_user(self, u_id):
		cur_id = None
		with self.db.cursor() as cur:
			cur.execute(f'SELECT current_q FROM users WHERE id={u_id};')
		cur_id = cur.fetchall()[0]['current_q']

		if cur_id:

			with self.db.cursor() as cur:
				cur.execute(f'SELECT u_id FROM uni_q WHERE id={cur_id};')

			return cur.fetchall()[0]

		else:
			return False

	def update_answers(self):
		excel_data = read_excel(f'{getcwd()}/answers.xlsx')
		data = DataFrame(excel_data, columns=['Вопрос', 'Ответ'])

		q = data['Вопрос']
		a = data['Ответ']

		with self.db.cursor() as cur:
			cur.execute(f'DELETE FROM answers;')

			for i in range(len(q)):
				cur.execute(f'INSERT INTO answers(q, a) VALUES("{q[i]}", "{a[i]}");')

		self.db.commit()

	def get_qs(self):
		with self.db.cursor() as cur:
			cur.execute(f'SELECT q FROM answers;')

		return [x['q'] for x in cur.fetchall()]

	def get_answers(self):
		with self.db.cursor() as cur:
			cur.execute(f'SELECT a FROM answers;')

		return [x['a'] for x in cur.fetchall()]

	def change_q(self, u_id):
		with self.db.cursor() as cur:
			cur.execute(f'SELECT current_q FROM users WHERE id={u_id};')

		cur_id = cur.fetchall()[0]['current_q']

		with self.db.cursor() as cur:
			cur.execute(f'SELECT id FROM uni_q WHERE id<>{cur_id};')

		qs = cur.fetchall()
		if len(qs) > 0:
			with self.db.cursor() as cur:
				cur.execute(f'UPDATE uni_q SET sended=0 where id={cur_id};')
				cur.execute(f'UPDATE users SET current_q={qs[0]["id"]} where id={u_id};')
				cur.execute(f'UPDATE uni_q SET sended=1 where id={qs[0]["id"]};')
				cur.execute(f'SELECT q FROM uni_q WHERE id={qs[0]["id"]};')

				return cur.fetchall()[0]['q']

		return False
