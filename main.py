import asyncio
import json

from aiogram import Bot, Dispatcher
from aiogram.types import Message

from config import token

bot = Bot(token)
dp = Dispatcher()

@dp.message()
async def cmd_start (message: Message):
    await message.answer ("!!!")


DATA_FILE = "messages.json"

def load_messages() -> list:
    if not json.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

def save_message(user_id: int, username: str, text: str):
    messages = load_messages()
    messages.append({
        "user_id": user_id,
        "username": username,
        "text": text,})
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

@dp.message()
async def handle(message: Message):
    #save_message(user_id=message.from_user.id,username=message.from_user.username or "no_username",text=message.text or "",)
    if message.audio:
        file_id = message.audio.file_id
        save_message(message.from_user.id, "voice", file_id)
        await message.answer("Голосовое сохранено!")
    else:
        await message.answer("Прочитал!")

@dp.message
async def cmd_start(message: Message):
    await message.answer("Ok")

async def main():
    await dp.start_polling(bot)

if __name__=='__main__':
    asyncio.run(main())
