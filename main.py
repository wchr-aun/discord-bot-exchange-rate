import asyncio
import logging
import time
from datetime import UTC, datetime
from functools import reduce

import discord
from discord.ext import commands, tasks

from channel.exchange import on_message as exchange_on_message
from external.ApiLayer import ExchangeAPI
from external.Blockchain import Blockchain
from external.FaithInOpenrent import FaithInOpenrent
from external.Firebase import Firebase
from setup import *

client = commands.Bot(command_prefix="", intents=discord.Intents.all())
exchange_client = ExchangeAPI(EXCHANGE_API)
firebase_client = Firebase(FIREBASE_SERVICE_ACCOUNT)
blockchain_client = Blockchain()
for_client = FaithInOpenrent()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user.name}.")
    logging.info("Starting...")
    ping_gpb_thb_rate.start()
    ping_mvrv.start()
    ping_for.start()


@tasks.loop(seconds=TIME_LOOP_API_LAYER)
async def ping_gpb_thb_rate():
    try:
        logging.info("-- Start pinging GBP-THB rate --")
        channel = client.get_channel(DISCORD_RATE_CHANNEL_ID)

        logging.info("EXCHANGE: Getting the rate")
        while True:
            rate = exchange_client.get_rates_thb()
            if rate is not None:
                break
            logging.warn(
                "EXCHANGE: Getting None from get_rates_thb() - sending a message and retrying later"
            )
            await channel.send("EXCHANGE: ⚠️ Had trouble getting rate... Retrying in 1 minute 🕛")
            time.sleep(60)
        logging.info(f"EXCHANGE: Successfully got the rate {rate}")

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        ping_list = firebase_client.get_profile_rates_less_than(rate)
        ping = (
            reduce(lambda acc, member_id: f"{acc} <@{member_id}>", ping_list, "\n\ncc.")
            if len(ping_list) != 0
            else ""
        )
        logging.info("EXCHANGE: Publishing the rate in Discord channel")
        await channel.send(
            f"🕛 {current_time} - The exchange rate is **{rate} THB/GBP**{ping}"
        )
        logging.info("-- Done pinging GBP-THB rate --")
    except Exception as e:
        logging.critical(e, exc_info=True)


@tasks.loop(seconds=TIME_LOOP_BTC_MVRV)
async def ping_mvrv():
    logging.info("-- Start pinging MVRV --")
    channel = client.get_channel(DISCORD_MVRV_CHANNEL_ID)
    mvrv_response = blockchain_client.get_mvrv()
    
    if mvrv_response == None:
        logging.warning("MVRV: MVRV response being None")
        logging.info("-- Done pinging MVRV --")
        return

    timestamp, mvrv = mvrv_response
    latest_mvrv_timestamp = firebase_client.get_latest_mvrv_timestamp()
    logging.info(latest_mvrv_timestamp)
    if timestamp > latest_mvrv_timestamp:
        firebase_client.set_latest_mvrv_timestamp(timestamp)
        await channel.send(f"{datetime.fromtimestamp(timestamp)} BTC MVRV - {mvrv}")
    else:
        logging.info("MVRV: No updates")
    logging.info("-- Done pinging MVRV --")


@tasks.loop(seconds=TIME_LOOP_FOR)
async def ping_for():
    logging.info("-- Start pinging FOR --")
    channel = client.get_channel(DISCORD_FOR_CHANNEL_ID)
    properties = for_client.get_for()
    for property in properties:
        if firebase_client.is_for_property_id_pinged(property["id"]):
            logging.info(f"FOR: Skip {property["id"]}")
            continue

        embed = discord.Embed(
            title=property["title"], description=property["description"]
        )
        embed.set_image(
            url=property['previewImage']
        )

        firebase_client.save_for_property_id(property['id'])

        await channel.send(
            content=f"Available on **{property['availableOn']}** for **£{property['price']}** *({property['lastUpdated']})* \n\n[Go to Openrent]({property['url']})",
            embed=embed,
        )
    logging.info("-- Done pinging FOR --")


@client.event
async def on_message(message):
    if message.channel.id == DISCORD_SETTING_CHANNEL_ID:
        return await exchange_on_message(message, client, firebase_client)
    return


@ping_gpb_thb_rate.before_loop
async def before_ping_gpb_thb_rate_loop():
    wait_time = EVERY_THREE_HOURS - datetime.now(UTC).timestamp() % (EVERY_THREE_HOURS)
    logging.info(f"Waiting {wait_time} seconds to ping_gpb_thb_rate")
    await asyncio.sleep(wait_time)
    logging.info("Finished waiting for ping_gpb_thb_rate")


@ping_mvrv.before_loop
async def before_ping_mvrv_loop():
    wait_time = EVERY_ONE_HOUR - datetime.now(UTC).timestamp() % (EVERY_ONE_HOUR)
    logging.info(f"Waiting {wait_time} seconds to start ping_mvrv")
    await asyncio.sleep(wait_time)
    logging.info("Finished waiting for ping_mvrv")


@ping_for.before_loop
async def before_ping_for_loop():
    wait_time = EVERY_THREE_HOURS - datetime.now(UTC).timestamp() % (EVERY_THREE_HOURS)
    logging.info(f"Waiting {wait_time} seconds to start ping_for")
    await asyncio.sleep(wait_time)
    logging.info("Finished waiting for ping_for")


client.run(TOKEN)
