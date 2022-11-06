import os

import discord
from discord.ext import tasks
from dotenv import load_dotenv
import requests
from datetime import datetime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
EXCHANGE_API = os.getenv('EXCHANGE_API')
DISCORD_ID = os.getenv('DISCORD_ID')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

TIME_LOOP = 24 * 60 * 60 / (250 // 30)

client = discord.Client(intents=discord.Intents.default())
exchange_url = 'https://api.apilayer.com/exchangerates_data/latest?symbols=THB&base=GBP'

def get_gbp_to_thb():
  payload = {}
  headers= {
    "apikey": EXCHANGE_API
  }

  response = requests.request("GET", exchange_url, headers=headers, data = payload)

  status_code = response.status_code
  if status_code != 200:
    return None
  return response.json()

def get_rates_thb():
  rates = get_gbp_to_thb()
  if rates is None:
    return None
  return rates['rates']['THB']

@client.event
async def on_ready():

    print(f'Logged in as {client.user.name}')
    channel = client.get_channel(CHANNEL_ID)
    await channel.send('Bot is ready!')
    ping_gpb_thb_rate.start()

@tasks.loop(seconds=TIME_LOOP)
async def ping_gpb_thb_rate():
    channel = client.get_channel(CHANNEL_ID)
    rate = get_rates_thb()
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    if rate is None:
        await channel.send('Error getting rate')
        return

    ping = f'<@{DISCORD_ID}>' if rate >= 44 else ''
    await channel.send(f'{current_time} - GBP to THB rate is {rate} {ping}')

client.run(TOKEN)