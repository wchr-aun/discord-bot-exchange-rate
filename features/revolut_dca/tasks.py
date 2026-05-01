import asyncio
import logging
from datetime import datetime, UTC

from discord.ext import tasks

from features.utils import attemptSending
from setup import (
    DISCORD_REVOLUT_CHANNEL_ID,
    REVOLUT_DCA_QUOTE_SIZE,
    TIME_LOOP_REVOLUT_DCA,
)
from .utils import (
    is_execution_day,
    get_seconds_to_next_execution_hour,
)

_bot = None
_revolut_client = None
_firebase_client = None


async def run_dca_logic():
    logging.info("Revolut DCA: Starting DCA logic execution")
    channel = _bot.get_channel(DISCORD_REVOLUT_CHANNEL_ID)

    now = datetime.now(UTC)
    # execution_date = now.strftime("%Y-%m-%d")
    execution_date = "2026-05-03"
    decision = _firebase_client.get_dca_skip_decision(execution_date)
    if decision and decision.get("state") == "SKIPPING":
        msg = f"Skipping DCA for {execution_date} as requested."
        logging.info("Revolut DCA: " + msg)
        if channel:
            await attemptSending(channel, "Revolut DCA", "⏭️ " + msg)

        # Update state to SKIPPED
        _firebase_client.set_dca_skip_decision(
            execution_date,
            {
                "state": "SKIPPED",
                "updated_at": datetime.now(UTC).isoformat(),
            },
        )
        return

    gbp_balance = _revolut_client.get_gbp_balance()
    if gbp_balance is None:
        msg = "Failed to fetch GBP balance."
        logging.error("Revolut DCA: " + msg)
        if channel:
            await attemptSending(channel, "Revolut DCA", "❌ " + msg)
        return

    if gbp_balance < float(REVOLUT_DCA_QUOTE_SIZE):
        msg = f"Insufficient balance. Available: £{gbp_balance}, Required: £{REVOLUT_DCA_QUOTE_SIZE}"
        logging.warning("Revolut DCA: " + msg)
        if channel:
            await attemptSending(channel, "Revolut DCA", "⚠️ " + msg)
        return

    order_response = _revolut_client.place_order(quote_size=str(REVOLUT_DCA_QUOTE_SIZE))
    if order_response:
        data = order_response.get("data", {})
        order_id = (
            data.get("venue_order_id")
            or data.get("client_order_id")
            or order_response.get("id")
        )
        msg = f"Successfully placed order `{order_id}` for £{REVOLUT_DCA_QUOTE_SIZE} worth of BTC."
        logging.info("Revolut DCA: " + msg)
        if channel:
            await attemptSending(channel, "Revolut DCA", "✅ " + msg)
    else:
        msg = "Revolut DCA: Failed to place order."
        logging.error("Revolut DCA: " + msg)
        if channel:
            await attemptSending(channel, "Revolut DCA", "❌ " + msg)


@tasks.loop(seconds=TIME_LOOP_REVOLUT_DCA)
async def revolut_dca_task():
    from setup import IS_PROD

    if IS_PROD:
        # In PROD, we run once every 24h. We check if it's the configured execution day.
        if not is_execution_day():
            logging.info(f"Revolut DCA: Today is not execution day, skipping.")
            return
    else:
        logging.info("Revolut DCA: Running loop (Non-PROD)")

    await run_dca_logic()


@revolut_dca_task.before_loop
async def before_revolut_dca_task():
    from setup import IS_PROD

    if IS_PROD:
        # Sync to next execution hour
        wait_time = get_seconds_to_next_execution_hour()
        logging.info(
            f"Revolut DCA: Waiting {wait_time} seconds to sync with execution hour"
        )
        await asyncio.sleep(wait_time)
        logging.info("Revolut DCA: Sync complete.")


def setup_tasks(bot, revolut_client, firebase_client):
    global _bot, _revolut_client, _firebase_client
    _bot = bot
    _revolut_client = revolut_client
    _firebase_client = firebase_client
    revolut_dca_task.start()
