import os

from dotenv import load_dotenv

load_dotenv()

IS_PROD = os.getenv("ENV") == "PROD"

TOKEN = os.getenv("DISCORD_TOKEN")
EXCHANGE_API = os.getenv("EXCHANGE_API")
DISCORD_ID = os.getenv("DISCORD_ID")

# Multi-currency support architecture
# Simply add more pairs here in the future: ["GBP-THB", "SGD-THB", ...]
EXCHANGE_PAIRS = ["GBP-THB"]


def get_rate_channel_id(pair: str = "GBP-THB"):
    # Defaulting to GBP-THB channel IDs for others if not specified in .env
    # To scale: add DISCORD_PAIRNAME_RATE_CHANNEL_ID to .env and handle here
    return (
        int(os.getenv("DISCORD_RATE_CHANNEL_ID"))
        if IS_PROD
        else int(os.getenv("DISCORD_DEV_RATE_CHANNEL_ID"))
    )


DISCORD_RATE_CHANNEL_ID = get_rate_channel_id("GBP-THB")

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
    "❗Invalid Command❗\n\nPlease use `!rate <pair> set <rate>` or `!rate <pair> get`"
)

DISCORD_MVRV_CHANNEL_ID = (
    int(os.getenv("DISCORD_MVRV_CHANNEL_ID"))
    if IS_PROD
    else int(os.getenv("DISCORD_DEV_MVRV_CHANNEL_ID"))
)
TIME_LOOP_BTC_MVRV = 60 * 60  # 1 hour
EVERY_ONE_HOUR = 60 * 60 if IS_PROD else 1

TIME_LOOP_FOR = 24 * 60 * 60
DISCORD_LOGS_CHANNEL_ID = (
    int(os.getenv("DISCORD_LOGS_CHANNEL_ID"))
    if IS_PROD
    else int(os.getenv("DISCORD_DEV_LOGS_CHANNEL_ID"))
)
DISCORD_LOGS_FLUSH_DELAY = 2  # seconds
EVERY_ONE_DAY = 24 * 60 * 60 if IS_PROD else 1

REVOLUT_PRIVATE_KEY = os.getenv("REVOLUT_PRIVATE_KEY")
REVOLUT_API_KEY = os.getenv("REVOLUT_API_KEY")
REVOLUT_DCA_QUOTE_SIZE = 60

DISCORD_REVOLUT_CHANNEL_ID = (
    int(os.getenv("DISCORD_REVOLUT_CHANNEL_ID") or 0)
    if IS_PROD
    else int(os.getenv("DISCORD_DEV_REVOLUT_CHANNEL_ID") or 0)
)
TIME_LOOP_REVOLUT_DCA = 24 * 60 * 60 if IS_PROD else 60

# DCA Schedule Configuration
REVOLUT_DCA_DAY_OF_WEEK = 6  # Sunday=6, Monday=0, etc.
REVOLUT_DCA_EXECUTION_HOUR = 4  # 4:00 AM UTC
