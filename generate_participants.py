import sqlite3
import random
import string

def create_users_table():
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()
    
    # Create the users table with added time columns
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            current_task INTEGER DEFAULT 1,
            time1 DATETIME, 
            time2 DATETIME,
            time3 DATETIME
        )
    ''')
    
    conn.commit()
    conn.close()


def generate_users(num_users):
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()

    for i in range(1, num_users + 1):
        user_id = 'user' + str(i)
        password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
        current_task = 1  # Or any default value you see fit

        c.execute('INSERT INTO users (user_id, password, current_task) VALUES (?, ?, ?)', (user_id, password, current_task,))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_users_table()
    generate_users(30)  # Generate 30 users
