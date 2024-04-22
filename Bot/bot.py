import asyncio
import logging
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from Configuration.bot_config import bot
from Bot.handlers import router, types


# list of available commands in bot
async def set_up_commands():
    bot_commands = [
        types.BotCommand(command="/start", description="Start Cinemate"),
        types.BotCommand(command="/help", description="Help"),
        types.BotCommand(command="/name_search", description="Search by name"),
        types.BotCommand(command="/filter_search", description="Search by criteria"),
        types.BotCommand(command="/recommend", description="Get recommendation"),
        types.BotCommand(command="/my_movielist", description="My movielist")
    ]
    await bot.set_my_commands(bot_commands)


async def main():
    await set_up_commands()
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
