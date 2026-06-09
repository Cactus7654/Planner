import sqlite3
from typing import Tuple, Optional

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
            regularity REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE (user_id, description)
        );        
        ''')
        conn.execute('''
               CREATE TABLE IF NOT EXISTS completions
               (
                   id          INTEGER PRIMARY KEY AUTOINCREMENT,
                   habit_id     INTEGER NOT NULL,
                   completed_at TEXT NOT NULL,
                   FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE,
                   UNIQUE (habit_id, completed_at)
               );        
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

#----------------сеттеры------------------
def add_habit(user_id, description, regularity):
    try:
        with get_db() as conn:
            conn.execute('''
            insert into habits (user_id, description, regularity) values(?, ?, ?) 
            ''', (user_id, description, regularity))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False


def add_completion(user_id, description, date_str):
    with get_db() as conn:
        hab = conn.execute('''
                SELECT id FROM habits WHERE user_id = ? AND description = ?''',
                     (user_id, description)).fetchone()
        if hab:
            conn.execute('''
            INSERT INTO completions
            (habit_id, completed_at) VALUES (?, ?)
            ''', (hab['id'], date_str))
            conn.commit()
            return True
        else:
            return False


def cancel_completion(user_id, description, date_str):
    with get_db() as conn:
        hab = conn.execute('''
                SELECT id FROM habits WHERE user_id = ? AND description = ?''',
                     (user_id, description)).fetchone()
        if hab:
            conn.execute('''
            DELETE FROM completions
            WHERE habit_id = ? and completed_at = ?
            ''', (hab['id'], date_str))
            conn.commit()
            return True
    return False


def delete_habit(user_id, id):
    with get_db() as conn:
       conn.execute('''
       DELETE FROM habits
       WHERE user_id = ?
       AND id = ?
       ''', (user_id, id))
       conn.commit()
       return True
    return False


def change_habit(new_regularity, new_description, user_id, id):
    with get_db() as conn:
       conn.execute('''
       UPDATE habits
       SET regularity = ?, description = ?
       WHERE user_id = ?
       AND id = ?
       ''', (new_regularity, new_description, user_id, id))
       conn.commit()
       return True
    return False



# отладочная
def get_last_execution_date(user_id, description):
    with get_db() as conn:
        hab = conn.execute('''
                SELECT id FROM habits WHERE user_id = ? AND description = ?''',
                     (user_id, description)).fetchone()
        if hab:
            result =  conn.execute('''
            SELECT completed_at
            FROM completions
            WHERE habit_id = ?
            ORDER BY completed_at DESC
            LIMIT 1
            ''', (hab['id'],)).fetchone()
            if result:
                return result['completed_at']
    return None

#----------------геттеры------------------

def get_all_habits(user_id):
    try:
        with get_db() as conn:
            return conn.execute('''
            select description, regularity, completed_at
            from habits h1
            LEFT JOIN completions c1
                ON h1.id = c1.habit_id
            where h1.user_id = ?
            ''', (user_id,)).fetchall()
    except sqlite3.Error as e:
        print(f'Ошибка при работе с бд:{e}')
        return False


def get_habits_for_dashboard(user_id):
    try:
        with get_db() as conn:
            return conn.execute('''
            select h1.id, description, regularity, MAX(completed_at) as completed_at
            from habits h1
            LEFT JOIN completions c1
                ON h1.id = c1.habit_id
            where h1.user_id = ?
            GROUP BY h1.id

            ''', (user_id,)).fetchall()
    except sqlite3.Error as e:
        print(f'Ошибка при работе с бд:{e}')
        return False


def get_last_completion(user_id, description) -> Optional[Tuple[str, str]]:
    try:
        with get_db() as conn:
            return conn.execute('''
            select regularity, completed_at
            from habits h1
            JOIN completions c1 ON h1.id = c1.habit_id
            where h1.user_id = ? AND h1.description = ?
            order by completed_at DESC
            LIMIT 1
            ''', (user_id, description)).fetchone()
    except sqlite3.Error as e:
        print(f'Ошибка при работе с бд:{e}')
        return None

#----------------на будущее------------------
def get_completions(user_id, description):
    try:
        with get_db() as conn:
            return conn.execute('''
            select regularity, completed_at
            from habits h1
            JOIN completions c1 ON h1.id = c1.habit_id
            where h1.user_id = ? AND h1.description = ?
            order by completed_at DESC
            ''', (user_id, description)).fetchall()
    except sqlite3.Error as e:
        print(f'Ошибка при работе с бд:{e}')
        return None


def drop():
    with get_db() as conn:
        conn.execute('drop table if exists habits')
        conn.execute('drop table if exists completions')