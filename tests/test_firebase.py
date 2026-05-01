import pytest
from unittest.mock import MagicMock, patch
from external.Firebase import Firebase


def test_firebase_set_profile_rates():
    fb = Firebase('{"dummy": "info"}')

    with patch("external.Firebase.IS_PROD", True):
        mock_db = fb.db
        mock_rates_col = mock_db.collection.return_value
        mock_pair_doc = mock_rates_col.document.return_value
        mock_profiles_col = mock_pair_doc.collection.return_value
        mock_user_doc = mock_profiles_col.document.return_value

        fb.set_profile_rates("user123", 45.0, pair="GBP-THB")

        mock_db.collection.assert_called_with("rates")
        mock_rates_col.document.assert_called_with("GBP-THB")
        mock_pair_doc.collection.assert_called_with("profiles")
        mock_profiles_col.document.assert_called_with("user123")
        mock_user_doc.set.assert_called_with({"rate": 45.0})


def test_firebase_get_profile_rates_exists():
    fb = Firebase('{"dummy": "info"}')

    mock_db = fb.db
    mock_doc = (
        mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value
    )
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"rate": 45.0}

    rate = fb.get_profile_rates("user123", pair="GBP-THB")
    assert rate == 45.0
