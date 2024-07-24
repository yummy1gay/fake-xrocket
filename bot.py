from telethon import TelegramClient, types, functions

from datetime import datetime

from config import api_id, api_hash
import os

client = TelegramClient('bot', api_id, api_hash)

start_time = datetime.now()

if not os.path.exists('users'):
    os.makedirs('users')

async def setup_bot_commands(client):
    print("[log] Добавляю команды боту...")
    commands = await client(
        functions.bots.GetBotCommandsRequest(
                scope=types.BotCommandScopeDefault(),
                lang_code=""
        )
    )

    if not commands:
        await client(
            functions.bots.SetBotCommandsRequest(
                scope=types.BotCommandScopeDefault(),
                lang_code="",
                commands=[
                    types.BotCommand(command="start", description="Main Menu"),
                    types.BotCommand(command="market", description="Market"),
                    types.BotCommand(command="wallet", description="Wallet"),
                    types.BotCommand(command="exchange", description="Exchange"),
                    types.BotCommand(command="settings", description="Settings"),
                    types.BotCommand(command="cheques", description="Cheques"),
                    types.BotCommand(command="invoices", description="Invoices"),
                    types.BotCommand(command="subscriptions", description="Subscriptions"),
                    types.BotCommand(command="rocketpay", description="RocketPay"),
                ],
            )
        )
        print("[log] Команды успешно добавлены!")
    else:
        print("[log] Команды у бота уже есть. Изменения не применены")