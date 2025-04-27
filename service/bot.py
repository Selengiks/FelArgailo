# service/bot.py

import os
from telethon import TelegramClient
from dotenv import load_dotenv
import sentry_sdk

load_dotenv()

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

class Bot(TelegramClient):
    def __init__(self):
        super().__init__("telethon", int(os.getenv("API_ID")), os.getenv("API_HASH"))
        self.channel = os.getenv("CHANNEL")
        self.service_chat_id = int(os.getenv("SERVICE_CHAT_ID"))
        self.test_channel = os.getenv("TEST_CHANNEL")
        self.test_chat_id = int(os.getenv("TEST_CHAT_ID"))
        self.allowed_users = [290522978, 472092975, 570477907, 582601743]
        self.temp_dir = ".\\temp"
        self.pixiv_access_token = os.getenv("PIXIV_ACCESS_TOKEN")
        self.pixiv_refresh_token = os.getenv("PIXIV_REFRESH_TOKEN")
        self.cobalt_url = os.getenv("COBALT_API_URL")
        self.cobalt_api_key = os.getenv("COBALT_API_KEY")

    def start_bot(self):
        self.start(password=lambda password: os.getenv("TWO_FACTOR_AUTH"))


bot = Bot()
