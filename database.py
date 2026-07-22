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
                category TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
        ''')


def add_expense(user_id: str, name: str, amount: int, category: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO expenses (user_id, name, amount, category) VALUES (?, ?, ?, ?)', (user_id, name, amount, category))


def get_user_expenses(user_id: str) -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, amount, category FROM expenses WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()

    expenses = []
    for row in rows:
        expenses.append({
            'id': row[0],
            'name': row[1],
            'amount': row[2],
            'category': row[3]
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


def get_extreme_expense(user_id: str, order: str):
    if order not in ('ASC', 'DESC'):
        raise ValueError("Invalid order")
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT id, name, amount, category FROM expenses WHERE user_id = ? ORDER BY amount {order} LIMIT 1', (user_id,))
        row = cursor.fetchone()

    if row is None:
        return None

    return {
        'id': row[0],
        'name': row[1],
        'amount': row[2],
        'category': row[3]
    }