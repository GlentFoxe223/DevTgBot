import sqlite3
class DBsearcher:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor=self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)''')
        self.conn.commit()

    def add_user(self, user_id, username):
        self.cursor.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?,?)',(user_id, username))
        self.conn.commit()

# class AI_DB:
#     def __init__(self, db_file):
#         self.conn = sqlite3.connect(db_file, check_same_thread=False)
#         self.cursor=self.conn.cursor()
#         self.create_table()

#     def create_table(self):
#         self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, bot_history TEXT)''')
#         self.conn.commit()
    
#     def add_user_history(self, user_id, history_message):
#         self.cursor.execute('INSERT OR IGNORE INTO users (user_id, bot_history) VALUES (?,?)',(user_id, history_message))
#         self.conn.commit()