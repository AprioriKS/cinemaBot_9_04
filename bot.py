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
from aiogram.types import Message, CallbackQuery, URLInputFile, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from comamands import (
    FILMS_COMMAND,
    FILM_CREATE,
    START_BOT_COMMAND,
    FILMS_BOT_COMMAND,
    FILM_CREATE_COMMAND,
)
from keyboards import films_keyboard_markup, FilmCallback
from models import Film
from state import FilmForm

dp = Dispatcher()


@dp.message(FILMS_COMMAND)
async def films(message: Message) -> None:
    data = get_films()
    markup = films_keyboard_markup(films_list=data)
    await message.answer(
        f"Перелік фільмів. Натисніть на назву фільму для деталей",
        reply_markup=markup
    )


@dp.message(FILM_CREATE)
async def film_create(message: Message, state: FSMContext) -> None:
    await state.set_state(FilmForm.name)
    await message.answer(f"Введіть назву фільму.", reply_markup=ReplyKeyboardRemove())


@dp.message(FilmForm.name)
async def film_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer(
        f"Введіть опис фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(FilmForm.description)


@dp.message(FilmForm.description)
async def film_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await message.answer(
        f"Вкажіть рейтинг фільму від 0 до 10.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(FilmForm.rating)


@dp.message(FilmForm.rating)
async def film_rating(message: Message, state: FSMContext) -> None:
    await state.update_data(rating=message.text)
    await message.answer(
        f"Введіть жанр фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(FilmForm.genre)


@dp.message(FilmForm.genre)
async def film_genre(message: Message, state: FSMContext) -> None:
    await state.update_data(genre=message.text)
    await message.answer(
        text=f"Введіть акторів фільму через роздільник ', '\n"
             + html.bold("Обов'язкова кома та відступ після неї."),
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(FilmForm.actors)


@dp.message(FilmForm.actors)
async def film_actors(message: Message, state: FSMContext) -> None:
    await state.update_data(actors=message.text.split(", "))
    await message.answer(
        f"Введіть посилання на постер фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(FilmForm.poster)


@dp.message(FilmForm.poster)
async def film_poster(message: Message, state: FSMContext) -> None:
    data = await state.update_data(poster=message.text)
    film_data = Film(**data)
    add_film(film_data.model_dump())
    await state.clear()
    await message.answer(f"Фільм {film_data.name} успішно додано", reply_markup=ReplyKeyboardRemove())

# aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: IMAGE_PROCESS_FAILED
# - ця помилка означає що передане посилання невірне(або екрановане).
# Рішенням буде заміна лінку на інший(БЕЗ КИРИЛИЦІ)


@dp.callback_query(FilmCallback.filter())
async def callb_film(callback: CallbackQuery, callback_data: FilmCallback) -> None:
    film_id = callback_data.id
    film_data = get_films(film_id=film_id)
    print(film_data)
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


def add_film(film: dict, file_path: str = "films.json"):
    films = get_films(file_path=file_path, film_id=None)
    if films:
        films.append(film)
        with open(file_path, "w", encoding="utf-8") as fp:
            json.dump(
                films,
                fp,
                indent=4,
                ensure_ascii=False,
            )


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await bot.set_my_commands([
        FILMS_BOT_COMMAND,
        START_BOT_COMMAND,
        FILM_CREATE_COMMAND,
    ]
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
