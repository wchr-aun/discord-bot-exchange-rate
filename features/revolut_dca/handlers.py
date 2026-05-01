import logging
from datetime import datetime, UTC
from setup import DISCORD_REVOLUT_CHANNEL_ID
from .utils import get_upcoming_execution_date_str

_bot = None
_firebase_client = None

async def on_message(message):
    if message.author.id == _bot.user.id:
        return
    if message.channel.id != DISCORD_REVOLUT_CHANNEL_ID:
        return
    if not message.content.startswith("/skip-dca"):
        return

    logging.info(f"Revolut DCA: Received command '{message.content}' from {message.author}")

    parts = message.content.split(" ")
    action = "SKIPPING"
    if len(parts) > 1 and parts[1].lower() == "cancel":
        action = "CANCELLED"

    execution_date = get_upcoming_execution_date_str()
    now = datetime.now(UTC).isoformat()
    
    existing = _firebase_client.get_dca_skip_decision(execution_date)
    
    if existing:
        data = {
            "updated_at": now,
            "by": message.author.id,
            "state": action
        }
    else:
        data = {
            "created_at": now,
            "updated_at": now,
            "execution_date": execution_date,
            "by": message.author.id,
            "state": action
        }
    
    _firebase_client.set_dca_skip_decision(execution_date, data)
    
    if action == "SKIPPING":
        await message.channel.send(f"⏭️ DCA for {execution_date} will be skipped.")
    else:
        await message.channel.send(f"✅ DCA skip for {execution_date} has been cancelled.")

def setup_handlers(bot, firebase_client):
    global _bot, _firebase_client
    _bot = bot
    _firebase_client = firebase_client
