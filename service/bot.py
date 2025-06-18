# service/bot.py

import os
from telethon import TelegramClient
from decouple import AutoConfig
import sentry_sdk

config = AutoConfig(".env" if os.path.exists(".env") else None)

sentry_sdk.init(
    dsn=config("SENTRY_DSN"),
    send_default_pii=True,
)

class Bot(TelegramClient):
    def __init__(self):
        super().__init__("telethon", int(config("API_ID")), config("API_HASH"))
        self.channel = config("CHANNEL")
        self.service_chat_id = int(config("SERVICE_CHAT_ID"))
        self.test_channel = config("TEST_CHANNEL")
        self.test_chat_id = int(config("TEST_CHAT_ID"))
        self.allowed_users = [290522978, 472092975, 570477907, 582601743]
        self.temp_dir = ".\\temp"
        self.pixiv_access_token = config("PIXIV_ACCESS_TOKEN")
        self.pixiv_refresh_token = config("PIXIV_REFRESH_TOKEN")
        self.cobalt_url = config("COBALT_API_URL")
        self.cobalt_api_key = config("COBALT_API_KEY")

    def start_bot(self):
        self.start(password=lambda password: config("TWO_FACTOR_AUTH"))


bot = Bot()
