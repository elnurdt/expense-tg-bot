import sqlite3

DB_PATH = 'expenses.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                name TEXT,
                amount INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
        ''')


def add_expense(user_id: str, name: str, amount: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO expenses (user_id, name, amount) VALUES (?, ?, ?)', (user_id, name, amount))


def get_user_expenses(user_id: str) -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, amount FROM expenses WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()

    expenses = []
    for row in rows:
        expenses.append({
            'id': row[0],
            'name': row[1],
            'amount': row[2]
        })

    return expenses        


def delete_expense(expense_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))


def clear_expenses(user_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE user_id = ?', (user_id,))