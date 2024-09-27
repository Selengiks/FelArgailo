# service/bot.py

import os
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()


class Bot(TelegramClient):
    def __init__(self):
        super().__init__("telethon", int(os.getenv("API_ID")), os.getenv("API_HASH"))
        self.channel = os.getenv("CHANNEL")
        self.service_chat_id = int(os.getenv("SERVICE_CHAT_ID"))
        self.test_channel = os.getenv("TEST_CHANNEL")
        self.test_chat_id = int(os.getenv("TEST_CHAT_ID"))
        self.allowed_users = [290522978, 472092975, 570477907]
        self.temp_dir = ".\\temp"
        self.pixiv_access_token = os.getenv("PIXIV_ACCESS_TOKEN")
        self.pixiv_refresh_token = os.getenv("PIXIV_REFRESH_TOKEN")

    def start_bot(self):
        self.start(password=lambda password: os.getenv("TWO_FACTOR_AUTH"))


bot = Bot()
