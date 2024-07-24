import asyncio

from handlers.message_handlers import *
from handlers.callback_handlers import *
from handlers.inline_handlers import *

from config import bot_token
from bot import setup_bot_commands, client

async def main():
    await client.start(bot_token=bot_token)
    await setup_bot_commands(client)
    print("[log] Бот запущен!")
    await client.run_until_disconnected()

asyncio.run(main())