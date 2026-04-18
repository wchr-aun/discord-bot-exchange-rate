import pytest
from unittest.mock import MagicMock, patch
from external.Firebase import Firebase

def test_firebase_set_profile_rates():
    # Firebase is already mocked in conftest.py's sys.modules
    fb = Firebase('{"dummy": "info"}')
    
    # Mock the db chain: fb.db.collection().document().set()
    mock_db = fb.db
    mock_collection = mock_db.collection.return_value
    mock_document = mock_collection.document.return_value
    
    fb.set_profile_rates("user123", 45.0)
    
    mock_db.collection.assert_called_with("profiles")
    mock_collection.document.assert_called_with("user123")
    mock_document.set.assert_called_with({"rate": 45.0})

def test_firebase_get_profile_rates_exists():
    fb = Firebase('{"dummy": "info"}')
    
    mock_db = fb.db
    mock_doc = mock_db.collection.return_value.document.return_value.get.return_value
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"rate": 45.0}
    
    rate = fb.get_profile_rates("user123")
    assert rate == 45.0

def test_firebase_get_profile_rates_not_exists():
    fb = Firebase('{"dummy": "info"}')
    
    mock_db = fb.db
    mock_doc = mock_db.collection.return_value.document.return_value.get.return_value
    mock_doc.exists = False
    
    rate = fb.get_profile_rates("user123")
    assert rate == float("inf")
