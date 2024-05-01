import os
from dotenv import load_dotenv
from .bot import Bot

from .db import connection, models

load_dotenv()


def main() -> None:
    connection.create_tables(models.all_models)
    bot = Bot(token=os.environ["TWITCH_ACCESS_TOKEN"], prefix="!")

    bot.run()
