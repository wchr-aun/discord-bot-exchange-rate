import logging
import asyncio
from setup import DISCORD_LOGS_FLUSH_DELAY

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
        await asyncio.sleep(DISCORD_LOGS_FLUSH_DELAY)
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
