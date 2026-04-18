import logging

from .handler import DiscordHandler


def setup(bot, channel_id):
    if not channel_id:
        return
        
    discord_handler = DiscordHandler(bot, channel_id)
    discord_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
    discord_handler.setFormatter(formatter)
    
    logging.getLogger().addHandler(discord_handler)
    
    # Return the handler so it can be used for immediate flushing if needed
    return discord_handler
