from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand

FILMS_COMMAND = Command("films")
FILM_CREATE = Command("create_film")

FILMS_BOT_COMMAND = BotCommand(command="films", description="Перегляд списку фільмів")
START_BOT_COMMAND = BotCommand(command="start", description="Start")
FILM_CREATE_COMMAND = BotCommand(command="create_film", description="Додати новий філььм")

