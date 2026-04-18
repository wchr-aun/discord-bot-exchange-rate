import pytest
from unittest.mock import AsyncMock, MagicMock
from channel.exchange import on_message

@pytest.mark.asyncio
async def test_on_message_set_rate():
    message = AsyncMock()
    message.author.id = 123
    message.content = "!rate set 45.5"
    message.channel.send = AsyncMock()
    
    client = MagicMock()
    client.user.id = 456
    
    firebase_client = MagicMock()
    
    await on_message(message, client, firebase_client)
    
    firebase_client.set_profile_rates.assert_called_once_with(123, 45.5)
    message.channel.send.assert_called_once_with(
        "<@123>'s rate notification is set to 45.5 THB/GBP 💰"
    )

@pytest.mark.asyncio
async def test_on_message_get_rate():
    message = AsyncMock()
    message.author.id = 123
    message.content = "!rate get"
    message.channel.send = AsyncMock()
    
    client = MagicMock()
    client.user.id = 456
    
    firebase_client = MagicMock()
    firebase_client.get_profile_rates.return_value = 45.5
    
    await on_message(message, client, firebase_client)
    
    firebase_client.get_profile_rates.assert_called_once_with(123)
    message.channel.send.assert_called_once_with(
        "<@123>'s rate notification is 45.5 THB/GBP 💰"
    )

@pytest.mark.asyncio
async def test_on_message_invalid_command():
    message = AsyncMock()
    message.author.id = 123
    message.content = "!rate invalid"
    message.channel.send = AsyncMock()
    
    client = MagicMock()
    client.user.id = 456
    
    firebase_client = MagicMock()
    
    from setup import INVALID_SETTING_MESSAGE
    
    await on_message(message, client, firebase_client)
    
    message.channel.send.assert_called_once_with(INVALID_SETTING_MESSAGE)
