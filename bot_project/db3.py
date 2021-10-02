import sqlite3

db = sqlite3.connect('server.db')
sql = db.cursor()
sql.execute('''CREATE TABLE IF NOT EXISTS users (
    name TEXT,
    age INT,
    expirience INT,
    komment, TEXT,
    location, TEXT
)''')

db.commit()


sql.execute(f"SELECT login FROM users WHERE login = '{user_login}'")
if sql.fetchone() is None:
    sql.execute(f"INSERT INTO users VALUES (?, ?, ?)", (user_login, user_password, 0))
    db.commit()
    print('зарегистрировано')

    for value in sql.execute('SELECT * FROM users'):
        print(value)