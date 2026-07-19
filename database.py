import sqlite3

DB_PATH = 'expenses.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    #Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            name TEXT,
            amount INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
                   )
''')
    
    #Save and close conection
    conn.commit()
    conn.close()


def add_expense(user_id: str, name: str, amount: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('INSERT INTO expenses (user_id, name, amount) VALUES (?, ?, ?)', (user_id, name, amount))

    conn.commit()
    conn.close()


def get_user_expenses(user_id: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, amount FROM expenses WHERE user_id = ?', (user_id,))
    
    rows = cursor.fetchall()
    
    conn.close()

    expenses = []
    for row in rows:
        expenses.append({
            'id': row[0],
            'name': row[1],
            'amount': row[2]
        })

    return expenses        


def delete_expense(expense_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))

    conn.commit()
    conn.close()


def clear_expenses(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM expenses WHERE user_id = ?', (user_id,))

    conn.commit()
    conn.close()