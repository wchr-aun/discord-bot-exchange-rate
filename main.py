import asyncio
import logging

import discord
from discord.ext import commands

from external.ApiLayer import ExchangeAPI
from external.Binance import BinanceApi
from external.Blockchain import Blockchain
from external.Firebase import Firebase
from external.Revolut import RevolutApi
from features.btc_mvrv import setup as setup_btc_mvrv
from features.exchange_rate import setup as setup_exchange_rate
from features.exchange_rate.handlers import on_message as on_exchange_rate_message
from features.logging import setup as setup_logging
from features.revolut_dca import setup as setup_revolut_dca
from features.utils import attemptSending
from setup import *

client = commands.Bot(command_prefix="", intents=discord.Intents.all())
exchange_client = ExchangeAPI(EXCHANGE_API)
firebase_client = Firebase(FIREBASE_SERVICE_ACCOUNT)
binance_client = BinanceApi()
blockchain_client = Blockchain()
revolut_client = (
    RevolutApi(REVOLUT_PRIVATE_KEY, REVOLUT_API_KEY)
    if REVOLUT_PRIVATE_KEY and REVOLUT_API_KEY
    else None
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)


@client.event
async def on_ready():
    logging.info(f"Service Started: Logged in as {client.user.name}.")

    # Send startup message directly to logs channel
    if DISCORD_LOGS_CHANNEL_ID:
        channel = client.get_channel(DISCORD_LOGS_CHANNEL_ID)
        if channel:
            client.loop.create_task(
                attemptSending(
                    channel,
                    "System",
                    f"🚀 Service Started: Logged in as `{client.user.name}`.",
                )
            )

            setup_logging(client, DISCORD_LOGS_CHANNEL_ID)

            logging.info("Starting features...")
    setup_exchange_rate(client, exchange_client, firebase_client)
    setup_btc_mvrv(client, blockchain_client, firebase_client, binance_client)
    setup_revolut_dca(client, revolut_client)

    logging.info("All features started.")


@client.event
async def on_message(message):
    await on_exchange_rate_message(message)


if __name__ == "__main__":
    client.run(TOKEN)
