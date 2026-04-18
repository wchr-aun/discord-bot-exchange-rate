import logging

async def attemptSending(channel, flow, message):
    try:
        await channel.send(f"{flow}: {message}")
    except Exception as e:
        logging.critical(f"{flow}: Unable to send discord message")
