import logging
from setup import (
    INVALID_SETTING_MESSAGE,
    DISCORD_SETTING_CHANNEL_ID,
    EXCHANGE_PAIRS,
    IS_PROD,
)

# Global clients to be set during setup()
_bot = None
_firebase_client = None


async def on_message(message):
    if message.author.id == _bot.user.id:
        return
    if message.channel.id != DISCORD_SETTING_CHANNEL_ID:
        return
    if not message.content.startswith("!rate"):
        return

    logging.info(f"Exchange Rate: Received command '{message.content}' from {message.author}")

    parts = message.content.split(" ")
    # Command patterns:
    # !rate set 45.5 (default GBP-THB)
    # !rate GBP-THB set 45.5
    # !rate get (default GBP-THB)
    # !rate GBP-THB get

    if len(parts) < 2:
        logging.warning(f"Exchange Rate: Invalid command length from {message.author}")
        await message.channel.send(INVALID_SETTING_MESSAGE)
        return

    pair = "GBP-THB"
    cmd_idx = 1
    
    # Check if the second part is a pair
    if parts[1].upper() in EXCHANGE_PAIRS:
        pair = parts[1].upper()
        cmd_idx = 2
    
    if len(parts) <= cmd_idx:
        logging.warning(f"Exchange Rate: Missing command after pair/prefix from {message.author}")
        await message.channel.send(INVALID_SETTING_MESSAGE)
        return

    command = parts[cmd_idx]
    profile_id = message.author.id

    if command == "set" and len(parts) == cmd_idx + 2:
        try:
            rate = float(parts[cmd_idx + 1])
            _firebase_client.set_profile_rates(profile_id, rate, pair=pair)
            logging.info(f"Exchange Rate: {'[MOCK] ' if not IS_PROD else ''}Set {pair} rate to {rate} for {message.author}")
            await message.channel.send(
                f"<@{profile_id}>'s {pair} rate notification is set to {rate} 💰"
            )
        except ValueError:
            logging.error(f"Exchange Rate: Invalid rate value '{parts[cmd_idx + 1]}' from {message.author}")
            await message.channel.send(INVALID_SETTING_MESSAGE)
    elif command == "get":
        rate = _firebase_client.get_profile_rates(profile_id, pair=pair)
        logging.info(f"Exchange Rate: {'[MOCK] ' if not IS_PROD else ''}Retrieved {pair} rate ({rate}) for {message.author}")
        await message.channel.send(
            f"<@{profile_id}>'s {pair} rate notification is {rate} 💰"
        )
    else:
        logging.warning(f"Exchange Rate: Unknown command '{command}' from {message.author}")
        await message.channel.send(INVALID_SETTING_MESSAGE)


def setup_handlers(bot, firebase_client):
    global _bot, _firebase_client
    _bot = bot
    _firebase_client = firebase_client
