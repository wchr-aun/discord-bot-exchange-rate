import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from main import ping_gpb_thb_rate, ping_mvrv

@pytest.mark.asyncio
async def test_ping_gpb_thb_rate():
    # Mocking external clients and discord channel
    with patch("main.exchange_client") as mock_exchange, \
         patch("main.firebase_client") as mock_firebase, \
         patch("main.client") as mock_discord_client:
        
        mock_channel = AsyncMock()
        mock_discord_client.get_channel.return_value = mock_channel
        mock_exchange.get_rates_thb.return_value = 45.0
        mock_firebase.get_profile_rates_less_than.return_value = ["user1", "user2"]
        
        # We need to call the underlying function of the task
        await ping_gpb_thb_rate()
        
        mock_exchange.get_rates_thb.assert_called()
        mock_channel.send.assert_called()
        args, _ = mock_channel.send.call_args
        assert "45.0 THB/GBP" in args[0]
        assert "<@user1>" in args[0]
        assert "<@user2>" in args[0]

@pytest.mark.asyncio
async def test_ping_mvrv():
    with patch("main.blockchain_client") as mock_blockchain, \
         patch("main.firebase_client") as mock_firebase, \
         patch("main.binance_client") as mock_binance, \
         patch("main.client") as mock_discord_client:
        
        mock_channel = AsyncMock()
        mock_discord_client.get_channel.return_value = mock_channel
        
        # Mocking mvrv response (timestamp, mvrv)
        mock_blockchain.get_mvrv.return_value = (1600000000, 2.5)
        mock_firebase.get_latest_mvrv_timestamp.return_value = 1500000000
        mock_binance.get_btc_price.return_value = "60000.0"
        
        await ping_mvrv()
        
        mock_firebase.set_latest_mvrv_timestamp.assert_called_with(1600000000)
        mock_channel.send.assert_called()
        args, _ = mock_channel.send.call_args
        assert "2.5" in args[0]
        assert "60000.0" in args[0]
