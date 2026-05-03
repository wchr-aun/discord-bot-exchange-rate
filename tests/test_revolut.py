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
    with patch("external.http_client.request") as mock_req:
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
    with patch("external.http_client.request") as mock_req:
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
    tasks._firebase_client = MagicMock()
    tasks._revolut_client.get_gbp_balance.return_value = 100.0

    # Mocking is_execution_day to return False (like a Monday)
    with patch("features.revolut_dca.tasks.is_execution_day", return_value=False):
        # Patch IS_PROD in setup module which is imported inside the task
        with patch("setup.IS_PROD", True):
            await revolut_dca_task()
            tasks._revolut_client.get_gbp_balance.assert_not_called()


@pytest.mark.asyncio
async def test_revolut_dca_task_runs_on_sunday(dummy_pem):
    from features.revolut_dca import tasks

    tasks._bot = MagicMock()
    tasks._revolut_client = MagicMock()
    tasks._firebase_client = MagicMock()
    tasks._firebase_client.get_dca_skip_decision.return_value = None
    tasks._revolut_client.get_gbp_balance.return_value = 100.0
    tasks._revolut_client.place_order.return_value = {
        "data": {"venue_order_id": "order_success", "state": "filled"}
    }

    mock_channel = MagicMock()
    tasks._bot.get_channel.return_value = mock_channel

    # Mocking is_execution_day to return True
    with patch("features.revolut_dca.tasks.is_execution_day", return_value=True):
        # Mocking datetime.now for run_dca_logic's date formatting
        with patch("features.revolut_dca.tasks.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime.datetime(
                2024, 5, 19, 4, 0, tzinfo=datetime.UTC
            )

            with patch("setup.IS_PROD", True):
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
async def test_revolut_dca_task_skips_if_firebase_says_so(dummy_pem):
    from features.revolut_dca import tasks

    tasks._bot = MagicMock()
    tasks._revolut_client = MagicMock()
    tasks._firebase_client = MagicMock()
    # Mock skip decision for today
    tasks._firebase_client.get_dca_skip_decision.return_value = {
        "state": "SKIPPING",
        "execution_date": "2024-05-19",
    }

    mock_channel = MagicMock()
    tasks._bot.get_channel.return_value = mock_channel

    # Mocking is_execution_day to return True
    with patch("features.revolut_dca.tasks.is_execution_day", return_value=True):
        # Mocking datetime.now to a Sunday (2024-05-19 is a Sunday)
        with patch("features.revolut_dca.tasks.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime.datetime(
                2024, 5, 19, 4, 0, tzinfo=datetime.UTC
            )

            with patch("setup.IS_PROD", True):
                with patch(
                    "features.revolut_dca.tasks.attemptSending", new_callable=AsyncMock
                ) as mock_send:
                    await revolut_dca_task()

                    # Should NOT call get_gbp_balance
                    tasks._revolut_client.get_gbp_balance.assert_not_called()
                    # Should update state to SKIPPED for TODAY
                    tasks._firebase_client.set_dca_skip_decision.assert_called_once()
                    args = tasks._firebase_client.set_dca_skip_decision.call_args[0]
                    assert args[0] == "2024-05-19"
                    assert args[1]["state"] == "SKIPPED"

                    mock_send.assert_called()
                    assert "Skipping DCA" in mock_send.call_args[0][2]


@pytest.mark.asyncio
async def test_revolut_dca_task_insufficient_balance(dummy_pem):
    from features.revolut_dca import tasks

    tasks._bot = MagicMock()
    tasks._revolut_client = MagicMock()
    tasks._firebase_client = MagicMock()
    tasks._firebase_client.get_dca_skip_decision.return_value = None
    tasks._revolut_client.get_gbp_balance.return_value = 10.0

    # Mocking is_execution_day to return True
    with patch("features.revolut_dca.tasks.is_execution_day", return_value=True):
        # Mocking datetime.now to a Sunday
        with patch("features.revolut_dca.tasks.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime.datetime(
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
