import asyncio
import datetime
import logging
from datetime import UTC

from discord.ext import tasks

from features.utils import attemptSending
from setup import (
    DISCORD_REVOLUT_CHANNEL_ID,
    IS_PROD,
    REVOLUT_DCA_QUOTE_SIZE,
    TIME_LOOP_REVOLUT_DCA,
)

_bot = None
_revolut_client = None


async def run_dca_logic():
    logging.info("Revolut DCA: Starting DCA logic execution")
    channel = _bot.get_channel(DISCORD_REVOLUT_CHANNEL_ID)

    gbp_balance = _revolut_client.get_gbp_balance()
    if gbp_balance is None:
        msg = "❌ Revolut DCA: Failed to fetch GBP balance."
        logging.error(msg)
        if channel:
            await attemptSending(channel, "Revolut DCA", msg)
        return

    if gbp_balance < float(REVOLUT_DCA_QUOTE_SIZE):
        msg = f"⚠️ Revolut DCA: Insufficient balance. Available: {gbp_balance} GBP, Required: {REVOLUT_DCA_QUOTE_SIZE} GBP"
        logging.warning(msg)
        if channel:
            await attemptSending(channel, "Revolut DCA", msg)
        return

    order_response = _revolut_client.place_order(quote_size=str(REVOLUT_DCA_QUOTE_SIZE))
    if order_response:
        data = order_response.get("data", {})
        order_id = (
            data.get("venue_order_id")
            or data.get("client_order_id")
            or order_response.get("id")
        )
        msg = f"✅ Revolut DCA: Successfully placed order for {REVOLUT_DCA_QUOTE_SIZE} GBP worth of BTC. Order ID: {order_id}"
        logging.info(msg)
        if channel:
            await attemptSending(channel, "Revolut DCA", msg)
    else:
        msg = "❌ Revolut DCA: Failed to place order."
        logging.error(msg)
        if channel:
            await attemptSending(channel, "Revolut DCA", msg)


@tasks.loop(seconds=TIME_LOOP_REVOLUT_DCA)
async def revolut_dca_task():
    from setup import IS_PROD

    if IS_PROD:
        # In PROD, we run once every 24h. We just need to check if it's Sunday.
        now = datetime.datetime.now(UTC)
        if now.weekday() != 6:
            logging.info(
                f"Revolut DCA: Today is weekday {now.weekday()}, skipping (waiting for Sunday=6)"
            )
            return
    else:
        logging.info("Revolut DCA: Running loop (Non-PROD)")

    await run_dca_logic()


@revolut_dca_task.before_loop
async def before_revolut_dca_task():
    from setup import IS_PROD

    if IS_PROD:
        # Sync to next 4:00 AM UTC
        now = datetime.datetime.now(UTC)
        target = now.replace(hour=4, minute=0, second=0, microsecond=0)
        if target <= now:
            target += datetime.timedelta(days=1)
        wait_time = (target - now).total_seconds()
        logging.info(
            f"Revolut DCA: Waiting {wait_time} seconds to sync with 4:00 AM UTC"
        )
        await asyncio.sleep(wait_time)
        logging.info("Revolut DCA: Sync complete.")


def setup_tasks(bot, revolut_client):
    global _bot, _revolut_client
    _bot = bot
    _revolut_client = revolut_client
    revolut_dca_task.start()
