import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message

token = "5849786205:AAFaagoy-H-oa3LMMNnObneFyA4lGB7GE74"
bot = Bot(token)

dp = Dispatcher()

@dp.message
async def Start (message:Message):
    await message.answer ("Hello")

async def main():
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())