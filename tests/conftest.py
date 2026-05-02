import os
from unittest.mock import MagicMock

import pytest

# Set up dummy environment variables for tests
os.environ["DISCORD_TOKEN"] = "dummy_token"
os.environ["EXCHANGE_API"] = "dummy_api"
os.environ["DISCORD_ID"] = "123456789"
os.environ["DISCORD_DEV_RATE_CHANNEL_ID"] = "111"
os.environ["DISCORD_DEV_SETTING_CHANNEL_ID"] = "222"
os.environ["FIREBASE_SERVICE_ACCOUNT"] = (
    '{"type": "service_account", "project_id": "dummy", "client_email": "dummy@dummy.com", "token_uri": "https://dummy.com", "private_key": "dummy_key"}'
)
os.environ["DISCORD_DEV_MVRV_CHANNEL_ID"] = "333"
os.environ["DISCORD_DEV_REVOLUT_CHANNEL_ID"] = "444"
os.environ["DISCORD_DEV_LOGS_CHANNEL_ID"] = "555"
os.environ["ENV"] = "DEV"

# Mock firebase_admin at the global level to avoid issues during imports
import sys
from unittest.mock import MagicMock

mock_firebase_admin = MagicMock()
mock_credentials = MagicMock()
mock_firestore = MagicMock()

sys.modules["firebase_admin"] = mock_firebase_admin
sys.modules["firebase_admin.credentials"] = mock_credentials
sys.modules["firebase_admin.firestore"] = mock_firestore

mock_credentials.Certificate.return_value = MagicMock()
mock_firebase_admin.initialize_app.return_value = MagicMock()
mock_firestore.client.return_value = MagicMock()


@pytest.fixture(autouse=True)
def firebase_mock():
    return mock_firestore.client.return_value
    return mock_firestore.client.return_value
