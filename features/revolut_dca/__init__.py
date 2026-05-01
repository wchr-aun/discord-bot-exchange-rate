from .tasks import setup_tasks


def setup(bot, revolut_client):
    setup_tasks(bot, revolut_client)
