import asyncio
import logging
import time
from datetime import datetime
from functools import reduce

import discord
from discord.ext import commands, tasks

from exchange_api import ExchangeAPI
from firebase import Firebase
from setup import *

client = commands.Bot(command_prefix="", intents=discord.Intents.all())
exchange_client = ExchangeAPI(EXCHANGE_API)
firebase_client = Firebase(FIREBASE_SERVICE_ACCOUNT)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user.name}.")
    logging.info("Starting...")
    ping_gpb_thb_rate.start()


@tasks.loop(seconds=TIME_LOOP)
async def ping_gpb_thb_rate():
    channel = client.get_channel(DISCORD_RATE_CHANNEL_ID)

    while True:
        rate = exchange_client.get_rates_thb()
        if rate is not None:
            break
        await channel.send("⚠️ Had trouble getting rate... Retrying in 1 minute 🕛")
        time.sleep(60)

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    ping_list = firebase_client.get_profile_rates_less_than(rate)
    ping = (
        reduce(lambda acc, member_id: f"{acc} <@{member_id}>", ping_list, "\n\ncc.")
        if len(ping_list) != 0
        else ""
    )
    await channel.send(
        f"🕛 {current_time} - The exchange rate is **{rate} THB/GBP**{ping}"
    )


@client.event
async def on_message(message):
    if (
        message.channel.id != DISCORD_SETTING_CHANNEL_ID
        or message.author.id == client.user.id
    ):
        return
    if not message.content.startswith("!rate"):
        await message.channel.send(INVALID_SETTING_MESSAGE)
        return
    if len(message.content.split(" ")) == 1:
        await message.channel.send(INVALID_SETTING_MESSAGE)
        return

    profile_id = message.author.id
    command = message.content.split(" ")[1]
    if command == "set" and len(message.content.split(" ")) == 3:
        rate = float(message.content.split(" ")[2])
        firebase_client.set_profile_rates(profile_id, rate)
        await message.channel.send(
            f"<@{profile_id}>'s rate notification is set to {rate} THB/GBP 💰"
        )
    elif command == "get":
        rate = firebase_client.get_profile_rates(profile_id)
        await message.channel.send(
            f"<@{profile_id}>'s rate notification is {rate} THB/GBP 💰"
        )
    else:
        await message.channel.send(INVALID_SETTING_MESSAGE)


@ping_gpb_thb_rate.before_loop
async def before_loop():
    wait_time = EVERY_THREE_HOURS - datetime.utcnow().timestamp() % (EVERY_THREE_HOURS)
    logging.info(f"Waiting {wait_time} seconds...")
    await asyncio.sleep(wait_time)
    logging.info("Finished waiting")


client.run(TOKEN)
