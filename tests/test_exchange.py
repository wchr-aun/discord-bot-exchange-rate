import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from features.exchange_rate.handlers import on_message

@pytest.mark.asyncio
async def test_on_message_set_rate_default():
    message = AsyncMock()
    message.author.id = 123
    message.content = "!rate set 45.5"
    message.channel.id = 222
    message.channel.send = AsyncMock()
    
    client = MagicMock()
    client.user.id = 456
    firebase_client = MagicMock()
    
    with patch("features.exchange_rate.handlers._bot", client), \
         patch("features.exchange_rate.handlers._firebase_client", firebase_client):
        await on_message(message)
    
    firebase_client.set_profile_rates.assert_called_once_with(123, 45.5, pair="GBP-THB")

@pytest.mark.asyncio
async def test_on_message_get_rate():
    message = AsyncMock()
    message.author.id = 123
    message.content = "!rate get"
    message.channel.id = 222
    message.channel.send = AsyncMock()
    
    client = MagicMock()
    client.user.id = 456
    firebase_client = MagicMock()
    firebase_client.get_profile_rates.return_value = 45.5
    
    with patch("features.exchange_rate.handlers._bot", client), \
         patch("features.exchange_rate.handlers._firebase_client", firebase_client):
        await on_message(message)
    
    firebase_client.get_profile_rates.assert_called_once_with(123, pair="GBP-THB")
