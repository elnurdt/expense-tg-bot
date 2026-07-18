import os
import json

DB_FILE_PATH = 'expenses.json'


def get_expenses():
    if not os.path.exists(DB_FILE_PATH):
        return {}
    
    with open(DB_FILE_PATH, 'r', encoding='utf-8') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}
        

def save_expenses(expenses):
    with open(DB_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(expenses, file, ensure_ascii=False, indent=4)   