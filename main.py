import discord
import asyncio
from functools import reduce
from datetime import datetime
from discord.ext import tasks
from exchange_api import ExchangeAPI
from firebase import Firebase
from setup import *

client = discord.Client(intents=discord.Intents.all())
exchange_client = ExchangeAPI(EXCHANGE_API)
firebase_client = Firebase(FIREBASE_SERVICE_ACCOUNT)

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}.')
    print('Starting...')
    ping_gpb_thb_rate.start()

@tasks.loop(seconds=TIME_LOOP)
async def ping_gpb_thb_rate():
    channel = client.get_channel(DISCORD_RATE_CHANNEL_ID)
    # rate = exchange_client.get_rates_thb()
    rate = 5
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    if rate is None:
        await channel.send('Error getting rate')
        return
    
    ping_list = firebase_client.get_profile_rates_less_than(rate)
    ping = reduce(lambda acc, member_id:  f'{acc} <@{member_id}>', ping_list, '\n\ncc.') if len(ping_list) != 0 else ''
    await channel.send(f'🕛 {current_time} - The exchange rate is **{rate} THB/GBP**{ping}')

@client.event
async def on_message(message):
    if message.channel.id != DISCORD_SETTING_CHANNEL_ID or message.author.id == client.user.id:
        return
    if not message.content.startswith('!rate'):
        await message.channel.send(INVALID_SETTING_MESSAGE)
        return
    if len(message.content.split(' ')) == 1:
        await message.channel.send(INVALID_SETTING_MESSAGE)
        return
    
    profile_id = message.author.id
    command = message.content.split(' ')[1]
    if command == 'set' and len(message.content.split(' ')) == 3:
        rate = float(message.content.split(' ')[2])
        firebase_client.set_profile_rates(profile_id, rate)
        await message.channel.send(f'<@{profile_id}>\'s rate notification is set to {rate} THB/GBP 💰')
    elif command == 'get':
        rate = firebase_client.get_profile_rates(profile_id)
        await message.channel.send(f'<@{profile_id}>\'s rate notification is {rate} THB/GBP 💰')
    else:
        await message.channel.send(INVALID_SETTING_MESSAGE)
    

@ping_gpb_thb_rate.before_loop
async def before_loop():
    wait_time = EVERY_THREE_HOURS - datetime.utcnow().timestamp() % (EVERY_THREE_HOURS)
    print(f'Waiting {wait_time} seconds...')
    await asyncio.sleep(wait_time)
    print('Finished waiting')

client.run(TOKEN)
