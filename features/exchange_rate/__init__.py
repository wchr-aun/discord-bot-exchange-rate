from .tasks import setup_tasks
from .handlers import setup_handlers


def setup(bot, exchange_client, firebase_client):
    setup_tasks(bot, exchange_client, firebase_client)
    setup_handlers(bot, firebase_client)
