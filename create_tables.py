import sqlite3

conn = sqlite3.connect('survey.db')
c = conn.cursor()

# Drop the existing tables if they exist
conn.execute('DROP TABLE IF EXISTS responses')
conn.execute('DROP TABLE IF EXISTS events')
conn.execute('DROP TABLE IF EXISTS users') # Adding this line to drop users table as well

# Create the responses table
c.execute('''
    CREATE TABLE responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        question TEXT NOT NULL,
        response TEXT NOT NULL,
        correct INTEGER, 
        ip_address TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

# Create the events table
c.execute('''
    CREATE TABLE events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        event_data TEXT NOT NULL,
        url TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

conn.commit()
conn.close()
