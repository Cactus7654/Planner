import sqlite3
from datetime import date

DATABASE = 'planner.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        ''')
        conn.execute('''
        CREATE TABLE IF NOT EXISTS habits
        (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            description TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            done        INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE (user_id, description, date)
        )
            
        
        ''')


init_db()


def register_user(username, password):
    try:
        with get_db() as conn:
            conn.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )
            return True
    except sqlite3.IntegrityError:
        return False


def check_user(username, password):
    with get_db() as conn:
        return conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()


def add_habit(user_id, description):
    today = date.today()
    try:
        with get_db() as conn:
            conn.execute('''
            insert into habits (user_id, description, date) values(?, ?, ?) 
            ''', (user_id, description, today))
            return True
    except sqlite3.IntegrityError:
        return False

