import asyncio
import logging
from aiogram import Dispatcher, types
from aiogram.filters.command import Command

from Configuration.bot_config import bot


# logging and dispatcher
logging.basicConfig(level=logging.INFO)
dp = Dispatcher()


# /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


# start polling
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
