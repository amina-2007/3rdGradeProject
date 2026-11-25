# ============================================================
# ИМПОРТЫ
# ============================================================
import asyncio
import json
import os  # ДОБАВЛЕНО: нужен для os.path.exists. В вашей версии
           # было json.path.exists, но у модуля json нет атрибута path,
           # бот упал бы с ошибкой при первом же сохранении.

# ДОБАВЛЕНО: F (магический фильтр) позволяет писать F.audio,
# то есть "обрабатывай только сообщения, где есть аудио".
from aiogram import Bot, Dispatcher, F

# ДОБАВЛЕНО: Command нужен, чтобы привязать обработчик к команде
# вроде /start или /list, а не ко всем сообщениям подряд.
from aiogram.filters import Command
from aiogram.types import Message

from config import token  # токен лежит в config.py, он в .gitignore

bot = Bot(token)
dp = Dispatcher()

# Файл, где хранятся сохранённые треки.
# Название "messages.json" оставлено ваше. Не забудьте добавить его в .gitignore.
DATA_FILE = "messages.json"


# ============================================================
# РАБОТА С ФАЙЛОМ ДАННЫХ
# ============================================================
def load_messages() -> list:
    # ИСПРАВЛЕНО: было json.path.exists -> стало os.path.exists.
    # Проверяем, существует ли файл. Если нет (первый запуск),
    # возвращаем пустой список.
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # Файл повреждён или не читается: не падаем, начинаем с пустого списка.
        return []


def save_message(user_id: int, username: str, text: str):
    # Читаем всё, что уже есть, добавляем новую запись и перезаписываем файл.
    # Для небольшого бота так просто и надёжно.
    messages = load_messages()
    messages.append({
        "user_id": user_id,
        "username": username,
        "text": text,  # в это поле мы кладём file_id трека
    })
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        # ensure_ascii=False, чтобы русские буквы не превращались в \u043f...
        json.dump(messages, f, ensure_ascii=False, indent=2)


# ============================================================
# ОБРАБОТЧИКИ
# ВАЖНО: aiogram проверяет обработчики сверху вниз и вызывает ПЕРВЫЙ
# подходящий. Поэтому конкретные (с фильтрами) идут вверху,
# а общий "ловит всё" стоит строго последним.
# ============================================================

# ИЗМЕНЕНО: добавлен фильтр Command("start").
# Раньше здесь был @dp.message() без фильтра, который отвечал "!!!"
# на ЛЮБОЕ сообщение и блокировал все остальные обработчики.
# Дубликат cmd_start внизу (с @dp.message без скобок) удалён:
# без () декоратор вообще не регистрирует обработчик правильно,
# а одинаковые имена функций затирают друг друга.
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Пришли мне аудиофайл, и я его сохраню. /list покажет твои треки.")


# ДОБАВЛЕНО: команда /list, чтобы бот возвращал сохранённые треки.
# Без неё сохранённые данные некуда было бы "проигрывать".
@dp.message(Command("list"))
async def cmd_list(message: Message):
    # Берём только записи текущего пользователя, чужие треки не показываем.
    tracks = [m for m in load_messages() if m["user_id"] == message.from_user.id]
    if not tracks:
        await message.answer("Пока пусто.")
        return
    for t in tracks:
        # answer_audio отправляет трек по file_id: файл заново
        # загружать не нужно, Telegram берёт его со своих серверов.
        await message.answer_audio(t["text"])


# ИЗМЕНЕНО: добавлен фильтр F.audio. Теперь обработчик срабатывает
# только когда в сообщении есть аудиофайл. Раньше стоял @dp.message()
# без фильтра, и внутри приходилось проверять message.audio через if/else.
@dp.message(F.audio)
async def handle_audio(message: Message):
    save_message(
        message.from_user.id,
        # ИСПРАВЛЕНО: раньше в username записывалось слово "voice",
        # хотя это не голосовое. Теперь настоящий username (или заглушка,
        # если у пользователя его нет).
        message.from_user.username or "no_username",
        message.audio.file_id,
    )
    await message.answer("Трек сохранён!")  # текст исправлен: это трек, не голосовое


# ДОБАВЛЕНО: общий обработчик без фильтра, ОБЯЗАТЕЛЬНО последний.
# Он отвечает только на то, что не подошло ни под один обработчик выше.
@dp.message()
async def fallback(message: Message):
    await message.answer("Пришли аудиофайл или используй /list")


# ============================================================
# ЗАПУСК
# ============================================================
async def main():
    # Запускаем polling: бот постоянно опрашивает Telegram о новых сообщениях.
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())