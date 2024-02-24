# service/bot.py

import os
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()


class Bot(TelegramClient):
    def __init__(self):
        super().__init__("telethon", int(os.getenv("API_ID")), os.getenv("API_HASH"))
        self.channel = os.getenv("CHANNEL")
        self.allowed_users = [290522978, 472092975, 570477907]

    def start_bot(self):
        self.start(password=lambda password: os.getenv("TWO_FACTOR_AUTH"))


bot = Bot()
