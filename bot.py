import asyncio
import logging
import sys
# from os import getenv
from config import BOT_TOKEN as TOKEN
import json

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, URLInputFile
from comamands import (
    FILMS_COMMAND,
    START_COMMAND,
    START_BOT_COMMAND,
    FILMS_BOT_COMMAND,
)
from keyboards import films_keyboard_markup, FilmCallback
from models import Film

dp = Dispatcher()


@dp.message(FILMS_COMMAND)
async def films(message: Message) -> None:
    data = get_films()
    markup = films_keyboard_markup(films_list=data)
    await message.answer(
        f"Перелік фільмів. Натисніть на назву фільму для деталей",
        reply_markup=markup
    )

@dp.callback_query(FilmCallback.filter())
async def callb_film(callback: CallbackQuery, callback_data: FilmCallback) -> None:
    film_id = callback_data.id
    film_data = get_films(film_id=film_id)
    film = Film(**film_data)

    text = f"Фільм: {film.name}\n" \
           f"Опис: {film.description}\n" \
           f"Рейтинг: {film.rating}\n" \
           f"Жанр: {film.genre}\n" \
           f"Актори: {', '.join(film.actors)}"

    await callback.message.answer_photo(
        caption=text,
        photo=URLInputFile(film.poster, filename=f"{film.name}_poster.{film.poster.split('.')[-1]}")
    )


@dp.message(CommandStart)
async def start(message: Message) -> None:
    await message.answer(
        f"Вітаю, {message.from_user.full_name}!\n"
        f"Я перший бот Python розробника Бугайова Костянтина!"
    )


def get_films(file_path: str = "films.json", film_id: int | None = None) -> list[dict] | dict:
    with open(file_path, "r", encoding="utf-8") as fp:
        films = json.load(fp)
        if film_id != None and film_id < len(films):
            return films[film_id]
        return films


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await bot.set_my_commands([
        FILMS_BOT_COMMAND,
        START_BOT_COMMAND,
    ]
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
