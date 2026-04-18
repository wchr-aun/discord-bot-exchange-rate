import asyncio
import logging
from datetime import UTC, datetime

from discord.ext import tasks

from features.utils import attemptSending
from setup import DISCORD_MVRV_CHANNEL_ID, EVERY_ONE_HOUR, TIME_LOOP_BTC_MVRV

# Global clients to be set during setup()
_bot = None
_blockchain_client = None
_firebase_client = None
_binance_client = None


@tasks.loop(seconds=TIME_LOOP_BTC_MVRV)
async def ping_mvrv():
    logging.info("-- Start pinging MVRV --")
    channel = _bot.get_channel(DISCORD_MVRV_CHANNEL_ID)
    mvrv_response = _blockchain_client.get_mvrv()

    if mvrv_response == None:
        logging.warning("MVRV: MVRV response being None")
        logging.info("-- Done pinging MVRV --")
        return

    timestamp, mvrv = mvrv_response
    latest_mvrv_timestamp = _firebase_client.get_latest_mvrv_timestamp()
    logging.info(f"Latest MVRV Timestamp: {latest_mvrv_timestamp}")
    btc_price = _binance_client.get_btc_price()
    if timestamp > latest_mvrv_timestamp:
        _firebase_client.set_latest_mvrv_timestamp(timestamp)
        await attemptSending(
            channel,
            "MVRV",
            f"{datetime.fromtimestamp(timestamp)} BTC MVRV - {mvrv}; BTC Price - {btc_price}",
        )
    else:
        logging.info("MVRV: No updates")
    logging.info("-- Done pinging MVRV --")


@ping_mvrv.before_loop
async def before_ping_mvrv_loop():
    wait_time = EVERY_ONE_HOUR - datetime.now(UTC).timestamp() % (EVERY_ONE_HOUR)
    logging.info(f"Waiting {wait_time} seconds to start ping_mvrv")
    await asyncio.sleep(wait_time)
    logging.info("Finished waiting for ping_mvrv")


def setup_tasks(bot, blockchain_client, firebase_client, binance_client):
    global _bot, _blockchain_client, _firebase_client, _binance_client
    _bot = bot
    _blockchain_client = blockchain_client
    _firebase_client = firebase_client
    _binance_client = binance_client
    ping_mvrv.start()
