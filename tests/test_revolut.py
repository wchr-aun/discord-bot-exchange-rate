import pytest
import datetime
from unittest.mock import MagicMock, patch, AsyncMock
from external.Revolut import RevolutApi
from features.revolut_dca.tasks import revolut_dca_task
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


@pytest.fixture
def dummy_pem():
    private_key = ed25519.Ed25519PrivateKey.generate()
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()


def test_revolut_get_gbp_balance_success(dummy_pem):
    api = RevolutApi(dummy_pem, "dummy_key")
    with patch("requests.request") as mock_req:
        mock_req.return_value.status_code = 200
        mock_req.return_value.json.return_value = [
            {"currency": "GBP", "available": "100.50"},
            {"currency": "USD", "available": "50.00"},
        ]

        with patch("external.Revolut.IS_PROD", True):
            balance = api.get_gbp_balance()
            assert balance == 100.50


def test_revolut_place_order_success(dummy_pem):
    api = RevolutApi(dummy_pem, "dummy_key")
    with patch("requests.request") as mock_req:
        mock_req.return_value.status_code = 201
        mock_req.return_value.json.return_value = {
            "data": {
                "venue_order_id": "order_123",
                "client_order_id": "client_123",
                "state": "filled",
            }
        }

        with patch("external.Revolut.IS_PROD", True):
            response = api.place_order(quote_size="60")
            assert response["data"]["venue_order_id"] == "order_123"


@pytest.mark.asyncio
async def test_revolut_dca_task_skips_if_not_sunday(dummy_pem):
    from features.revolut_dca import tasks

    tasks._bot = MagicMock()
    tasks._revolut_client = MagicMock()
    tasks._revolut_client.get_gbp_balance.return_value = 100.0

    # Mocking datetime to a Monday (2024-05-20 is a Monday)
    with patch("features.revolut_dca.tasks.datetime") as mock_datetime:
        mock_datetime.datetime.now.return_value = datetime.datetime(
            2024, 5, 20, 4, 0, tzinfo=datetime.UTC
        )

        # Patch IS_PROD in setup module which is imported inside the task
        with patch("setup.IS_PROD", True):
            await revolut_dca_task()
            tasks._revolut_client.get_gbp_balance.assert_not_called()


@pytest.mark.asyncio
async def test_revolut_dca_task_runs_on_sunday(dummy_pem):
    from features.revolut_dca import tasks

    tasks._bot = MagicMock()
    tasks._revolut_client = MagicMock()
    tasks._revolut_client.get_gbp_balance.return_value = 100.0
    tasks._revolut_client.place_order.return_value = {
        "data": {"venue_order_id": "order_success", "state": "filled"}
    }

    mock_channel = MagicMock()
    tasks._bot.get_channel.return_value = mock_channel

    # Mocking datetime to a Sunday (2024-05-19 is a Sunday)
    with patch("features.revolut_dca.tasks.datetime") as mock_datetime:
        mock_datetime.datetime.now.return_value = datetime.datetime(
            2024, 5, 19, 4, 0, tzinfo=datetime.UTC
        )

        with patch("features.revolut_dca.tasks.IS_PROD", True):
            with patch(
                "features.revolut_dca.tasks.attemptSending", new_callable=AsyncMock
            ) as mock_send:
                await revolut_dca_task()
                tasks._revolut_client.get_gbp_balance.assert_called_once()
                tasks._revolut_client.place_order.assert_called_once_with(
                    quote_size="60"
                )
                mock_send.assert_called()
                assert "Successfully placed order" in mock_send.call_args[0][2]


@pytest.mark.asyncio
async def test_revolut_dca_task_insufficient_balance(dummy_pem):
    from features.revolut_dca import tasks

    tasks._bot = MagicMock()
    tasks._revolut_client = MagicMock()
    tasks._revolut_client.get_gbp_balance.return_value = 10.0

    # Mocking datetime to a Sunday
    with patch("features.revolut_dca.tasks.datetime") as mock_datetime:
        mock_datetime.datetime.now.return_value = datetime.datetime(
            2024, 5, 19, 4, 0, tzinfo=datetime.UTC
        )

        with patch(
            "features.revolut_dca.tasks.attemptSending", new_callable=AsyncMock
        ) as mock_send:
            await revolut_dca_task()

            tasks._revolut_client.get_gbp_balance.assert_called_once()
            tasks._revolut_client.place_order.assert_not_called()
            mock_send.assert_called()
            assert "Insufficient balance" in mock_send.call_args[0][2]
