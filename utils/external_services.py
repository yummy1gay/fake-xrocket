import requests
import random
import string
import os

from bot import client
from config import admin_id

def get_ton_usd_price():
    response = requests.get("https://tonapi.io/v2/rates?tokens=TON&currencies=USD")
    data = response.json()
    ton_usd_price = float(data["rates"]["TON"]["prices"]["USD"])
    return ton_usd_price

def generate_cheque_id():
    return 't_' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

async def send_newsletter(message):
    for filename in os.listdir('users'):
        user_id = int(filename.split('.')[0])
        if user_id != admin_id:
            await client.send_message(user_id, message)

def format_balance(balance):
    return int(balance) if balance.is_integer() else balance