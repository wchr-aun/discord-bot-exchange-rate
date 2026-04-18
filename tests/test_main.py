import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from features.exchange_rate.tasks import ping_rates
from features.btc_mvrv.tasks import ping_mvrv

@pytest.mark.asyncio
async def test_ping_rates():
    mock_exchange = MagicMock()
    mock_firebase = MagicMock()
    mock_bot = MagicMock()
    
    mock_channel = AsyncMock()
    mock_bot.get_channel.return_value = mock_channel
    mock_exchange.get_rate.return_value = 45.0
    mock_firebase.get_profile_rates_less_than.return_value = ["user1", "user2"]
    
    with patch("features.exchange_rate.tasks._bot", mock_bot), \
         patch("features.exchange_rate.tasks._exchange_client", mock_exchange), \
         patch("features.exchange_rate.tasks._firebase_client", mock_firebase), \
         patch("features.exchange_rate.tasks.EXCHANGE_PAIRS", ["GBP-THB"]):
        await ping_rates()
        
    mock_exchange.get_rate.assert_called_with("GBP", "THB")
    mock_channel.send.assert_called()
    args, _ = mock_channel.send.call_args
    assert "45.0 THB/GBP" in args[0]

@pytest.mark.asyncio
async def test_ping_mvrv():
    mock_blockchain = MagicMock()
    mock_firebase = MagicMock()
    mock_binance = MagicMock()
    mock_bot = MagicMock()
    
    mock_channel = AsyncMock()
    mock_bot.get_channel.return_value = mock_channel
    
    # Mocking mvrv response (timestamp, mvrv)
    mock_blockchain.get_mvrv.return_value = (1600000000, 2.5)
    mock_firebase.get_latest_mvrv_timestamp.return_value = 1500000000
    mock_binance.get_btc_price.return_value = "60000.0"
    
    with patch("features.btc_mvrv.tasks._bot", mock_bot), \
         patch("features.btc_mvrv.tasks._blockchain_client", mock_blockchain), \
         patch("features.btc_mvrv.tasks._firebase_client", mock_firebase), \
         patch("features.btc_mvrv.tasks._binance_client", mock_binance):
        await ping_mvrv()
        
    mock_firebase.set_latest_mvrv_timestamp.assert_called_with(1600000000)
    mock_channel.send.assert_called()
    args, _ = mock_channel.send.call_args
    assert "2.5" in args[0]
    assert "60000.0" in args[0]
