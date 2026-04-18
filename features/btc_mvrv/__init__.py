from .tasks import setup_tasks


def setup(bot, blockchain_client, firebase_client, binance_client):
    setup_tasks(bot, blockchain_client, firebase_client, binance_client)
