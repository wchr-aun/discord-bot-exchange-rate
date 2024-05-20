import os

from dotenv import load_dotenv

load_dotenv()

IS_PROD = os.getenv("ENV") == "PROD"

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
EXCHANGE_API = os.getenv("EXCHANGE_API")
DISCORD_ID = os.getenv("DISCORD_ID")
DISCORD_RATE_CHANNEL_ID = (
    int(os.getenv("DISCORD_RATE_CHANNEL_ID"))
    if IS_PROD
    else int(os.getenv("DISCORD_DEV_RATE_CHANNEL_ID"))
)
DISCORD_SETTING_CHANNEL_ID = (
    int(os.getenv("DISCORD_SETTING_CHANNEL_ID"))
    if IS_PROD
    else int(os.getenv("DISCORD_DEV_SETTING_CHANNEL_ID"))
)
FIREBASE_SERVICE_ACCOUNT = os.getenv("FIREBASE_SERVICE_ACCOUNT")

TIME_LOOP_API_LAYER = (
    24 * 60 * 60 / (250 // 30)
)  # 250 Free API calls a month; divided it into calls per day
EVERY_THREE_HOURS = 60 * 60 * 3 if IS_PROD else 1
INVALID_SETTING_MESSAGE = (
    "❗Invalid Command❗\n\nPlease use `!rate set <rate>` or `!rate get`"
)

DISCORD_MVRV_CHANNEL_ID = (
    int(os.getenv("DISCORD_MVRV_CHANNEL_ID"))
    if IS_PROD
    else int(os.getenv("DISCORD_DEV_MVRV_CHANNEL_ID"))
)
TIME_LOOP_BTC_MVRV = 60 * 60  # 1 hour
EVERY_ONE_HOUR = 60 * 60 if IS_PROD else 1
