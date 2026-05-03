import asyncio
import logging
import time
from datetime import UTC, datetime
from functools import reduce
from discord.ext import tasks
from features.utils import attemptSending
from setup import (
    TIME_LOOP_API_LAYER,
    EVERY_THREE_HOURS,
    EXCHANGE_PAIRS,
    get_rate_channel_id,
)

# Global clients to be set during setup()
_bot = None
_exchange_client = None
_firebase_client = None


@tasks.loop(seconds=TIME_LOOP_API_LAYER)
async def ping_rates():
    for pair in EXCHANGE_PAIRS:
        try:
            base, symbol = pair.split("-")
            logging.info(f"-- Start pinging {pair} rate --")
            channel_id = get_rate_channel_id(pair)
            channel = _bot.get_channel(channel_id)

            logging.info(f"EXCHANGE: Getting the {pair} rate")
            rate = _exchange_client.get_rate(base, symbol)
            
            if rate is None:
                logging.warning(
                    f"EXCHANGE: Getting None from get_rate({pair}) after retries - skipping this cycle"
                )
                continue
                
            logging.info(f"EXCHANGE: Successfully got the {pair} rate {rate}")

            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            ping_list = _firebase_client.get_profile_rates_less_than(rate, pair=pair)
            ping = (
                reduce(lambda acc, member_id: f"{acc} <@{member_id}>", ping_list, "\n\ncc.")
                if len(ping_list) != 0
                else ""
            )
            logging.info(f"EXCHANGE: Publishing the {pair} rate in Discord channel")
            await attemptSending(
                channel,
                "EXCHANGE",
                f"🕛 {current_time} - The exchange rate is **{rate} {symbol}/{base}**{ping}",
            )
            logging.info(f"-- Done pinging {pair} rate --")
        except Exception as e:
            logging.critical(e, exc_info=True)


@ping_rates.before_loop
async def before_ping_rates_loop():
    wait_time = EVERY_THREE_HOURS - datetime.now(UTC).timestamp() % (EVERY_THREE_HOURS)
    logging.info(f"Waiting {wait_time} seconds to ping_rates")
    await asyncio.sleep(wait_time)
    logging.info("Finished waiting for ping_rates")


def setup_tasks(bot, exchange_client, firebase_client):
    global _bot, _exchange_client, _firebase_client
    _bot = bot
    _exchange_client = exchange_client
    _firebase_client = firebase_client
    ping_rates.start()
