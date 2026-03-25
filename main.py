from os import getenv
import asyncio
from aiogram import Dispatcher, Bot
from handlers.commands import rout
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
dp.include_router(rout)



async def main():
    bot = Bot(token = TOKEN)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())