import json
import os

from config import balance_ton, balance_usdt

def load_user_data(user_id):
    file_path = f'users/{user_id}.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return None

def save_user_data(user_id, data):
    file_path = f'users/{user_id}.json'
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def create_new_user(user_id, first_name, last_name, username):
    user_data = {
        "id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "balance_ton": float(balance_ton),
        "balance_usdt": float(balance_usdt),
        "creating_cheque": False,
        "creating_cheque_currency": None,
        "adding_comment": False,
        "adding_comment_inline": None,
        "locking_cheque": None,
        "last_message_id": None,
        "cheques": []
    }
    save_user_data(user_id, user_data)
    return user_data