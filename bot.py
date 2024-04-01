import asyncio
import logging
from aiogram import Dispatcher, types
from aiogram.filters.command import Command

from Configuration.bot_config import bot

# logging and dispatcher
logging.basicConfig(level=logging.INFO)
dp = Dispatcher()


# list of available commands in bot
async def set_up_commands():
    bot_commands = [
        types.BotCommand(command="/start", description="Start Cinemate"),
        types.BotCommand(command="/help", description="Help"),
        types.BotCommand(command="/name_search", description="Search by name"),
        types.BotCommand(command="/filter_search", description="Search by criteria"),
        types.BotCommand(command="/recommend", description="Get recommendation"),
        types.BotCommand(command="/my_movielist", description="My movielist"),
        types.BotCommand(command="/info", description="Get information for the current film")

    ]
    await bot.set_my_commands(bot_commands)


# /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


# start polling
async def main():
    await set_up_commands()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
