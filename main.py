import logging

import discord
from discord.ext import commands

from external.ApiLayer import ExchangeAPI
from external.Binance import BinanceApi
from external.Blockchain import Blockchain
from external.Firebase import Firebase
from setup import *
from features.exchange_rate import setup as setup_exchange_rate
from features.btc_mvrv import setup as setup_btc_mvrv

client = commands.Bot(command_prefix="", intents=discord.Intents.all())
exchange_client = ExchangeAPI(EXCHANGE_API)
firebase_client = Firebase(FIREBASE_SERVICE_ACCOUNT)
binance_client = BinanceApi()
blockchain_client = Blockchain()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user.name}.")
    logging.info("Starting features...")
    
    setup_exchange_rate(client, exchange_client, firebase_client)
    setup_btc_mvrv(client, blockchain_client, firebase_client, binance_client)
    
    logging.info("All features started.")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        if ctx.message.content.startswith("!rate"):
            logging.info(f"Ignoring CommandNotFound for !rate - handled by listener")
            return
    raise error


if __name__ == "__main__":
    client.run(TOKEN)
