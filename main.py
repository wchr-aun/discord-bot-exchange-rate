import logging
import asyncio

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

class DiscordHandler(logging.Handler):
    def __init__(self, bot, channel_id):
        super().__init__()
        self.bot = bot
        self.channel_id = channel_id
        self.buffer = []
        self._flush_task = None
        self._lock = asyncio.Lock()

    def emit(self, record):
        if self.bot.is_closed():
            return
        
        # Avoid infinite recursion
        if record.name.startswith('discord'):
            return

        log_entry = self.format(record)
        self.buffer.append(log_entry)

        if self._flush_task is None or self._flush_task.done():
            if self.bot.loop.is_running():
                self._flush_task = self.bot.loop.create_task(self._wait_and_flush())

    async def _wait_and_flush(self):
        await asyncio.sleep(5)
        await self.flush_buffer()

    async def flush_buffer(self):
        async with self._lock:
            if not self.buffer:
                return
            logs_to_send = list(self.buffer)
            self.buffer = []

        try:
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                channel = await self.bot.fetch_channel(self.channel_id)
            
            if channel:
                # Group logs into chunks of 2000 characters
                current_batch = "```\n"
                for entry in logs_to_send:
                    # If entry itself is > 1900, truncate it
                    if len(entry) > 1900:
                        entry = entry[:1900] + "... (truncated)"
                    
                    if len(current_batch) + len(entry) + 5 > 2000:
                        await channel.send(current_batch + "```")
                        current_batch = "```\n"
                    
                    current_batch += entry + "\n"
                
                if current_batch != "```\n":
                    await channel.send(current_batch + "```")
        except Exception:
            # Fallback to prevent logging errors from crashing the app
            pass


@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user.name}.")
    
    if DISCORD_LOGS_CHANNEL_ID:
        discord_handler = DiscordHandler(client, DISCORD_LOGS_CHANNEL_ID)
        discord_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        discord_handler.setFormatter(formatter)
        logging.getLogger().addHandler(discord_handler)
        logging.info("Discord logging handler added with 5s buffering.")

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
