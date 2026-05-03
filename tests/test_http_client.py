import pytest
import requests
from unittest.mock import MagicMock, patch
from external import http_client
from urllib3.util.retry import Retry

def test_request_success():
    with patch("external.http_client._default_session.request") as mock_req:
        mock_req.return_value.status_code = 200
        mock_req.return_value.json.return_value = {"status": "ok"}
        
        response = http_client.request("GET", "https://api.example.com")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_req.assert_called_once()

def test_request_default_timeout():
    with patch("external.http_client._default_session.request") as mock_req:
        http_client.request("GET", "https://api.example.com")
        # Check that timeout=15 was passed if not provided
        _, kwargs = mock_req.call_args
        assert kwargs["timeout"] == 15

def test_request_custom_timeout():
    with patch("external.http_client._default_session.request") as mock_req:
        http_client.request("GET", "https://api.example.com", timeout=30)
        _, kwargs = mock_req.call_args
        assert kwargs["timeout"] == 30

def test_retry_configuration():
    """
    Verify that the retry session is correctly configured with LoggingRetry.
    """
    session = http_client.get_retry_session(retries=5, backoff_factor=2)
    adapter = session.get_adapter("https://")
    
    assert isinstance(adapter.max_retries, http_client.LoggingRetry)
    assert adapter.max_retries.total == 5
    assert adapter.max_retries.connect == 5
    assert adapter.max_retries.read == 5
    assert adapter.max_retries.backoff_factor == 2
    assert 500 in adapter.max_retries.status_forcelist
    assert 502 in adapter.max_retries.status_forcelist
    assert 503 in adapter.max_retries.status_forcelist
    assert 504 in adapter.max_retries.status_forcelist

def test_custom_retry_config_integration():
    """
    Verify that passing retry_config to request() uses a new session with those settings.
    """
    with patch("external.http_client.get_retry_session") as mock_get_session:
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        retry_config = {"retries": 10, "backoff_factor": 0.5}
        http_client.request("GET", "https://api.example.com", retry_config=retry_config)
        
        mock_get_session.assert_called_once_with(retries=10, backoff_factor=0.5)
        mock_session.request.assert_called_once()
