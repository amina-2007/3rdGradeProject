import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

from config import TOKEN

logging.basicConfig(level=logging.INFO) # для фиксирования ошибок

bot = Bot(TOKEN) # хранение токена в отдельном файле
dp = Dispatcher()

@dp.message(CommandStart()) # ну это команда, поэтому скобки (а так команда /start)
async def start (message:Message):
    await message.answer ("Hello")

async def main():
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())
