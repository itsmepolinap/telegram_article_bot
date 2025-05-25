import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from dotenv import load_dotenv

from link_store import LinkStorage, LinkAlreadyExists
from utils import check_url_format

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
DB_FILE = "user_data.db"

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


@dp.message(CommandStart())
async def welcome_user(message: Message):
    await message.answer(
        "👋 Привет! Отправь мне ссылку, и я её сохраню. "
        "Чтобы получить случайную — напиши /get_article."
    )


@dp.message(Command("get_article"))
async def provide_random_article(message: Message):
    user_id = message.from_user.id
    async with LinkStorage(DB_FILE) as storage:
        link = await storage.pop_random_link(user_id)
        if link:
            await message.answer(f"Время прочитать:\n{link}")
        else:
            await message.answer("У вас пока нет сохранённых ссылок.")


@dp.message()
async def handle_text_message(message: Message):
    url_candidate = message.text.strip()
    user_id = message.from_user.id

    if not check_url_format(url_candidate):
        await message.reply("Это не похоже на правильную ссылку.")
        return

    async with LinkStorage(DB_FILE) as storage:
        try:
            await storage.insert_link(user_id, url_candidate)
            await message.reply("Ссылка добавлена!")
        except LinkAlreadyExists:
            await message.reply("Такая ссылка уже есть в вашем списке.")


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
