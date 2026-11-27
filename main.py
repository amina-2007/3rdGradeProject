import asyncio
import json
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command


from config import token

bot = Bot(token)
dp = Dispatcher()

DATA_FILE = "messages.json"

def load_messages() -> list:
    if not os.path.exists(DATA_FILE):
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
        "text": text,
    })
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Пришли мне аудиофайл, и я его сохраню. /list покажет твои треки.")

@dp.message(Command("list"))
async def cmd_list(message: Message):
    tracks = [m for m in load_messages() if m["user_id"] == message.from_user.id]
    if not tracks:
        await message.answer("Пока пусто.")
        return
    for t in tracks:
        await message.answer_audio(t["text"])

@dp.message(F.audio)
async def handle_audio(message: Message):
    save_message(
        message.from_user.id,
        message.from_user.username or "no_username",
        message.audio.file_id,
    )
    await message.answer("Трек сохранён!")

@dp.message()
async def fallback(message: Message):
    await message.answer("Пришли аудиофайл или используй /list")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
