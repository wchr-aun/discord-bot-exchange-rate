import json
import logging

from firebase_admin import credentials, firestore, initialize_app

from setup import IS_PROD


class Firebase:
    def __init__(self, service_account: str) -> None:
        SERVICE_ACCOUNT = service_account
        cred = credentials.Certificate(json.loads(SERVICE_ACCOUNT))
        initialize_app(cred)
        self.db = firestore.client()

    def _get_profile_collection(self, pair: str = "GBP-THB"):
        # We can structure it by pair to allow scaling
        return self.db.collection("rates").document(pair).collection("profiles")

    def set_profile_rates(self, profile_id: str, rate: float, pair: str = "GBP-THB") -> None:
        if not IS_PROD:
            logging.info(f"Mocking set_profile_rates: {profile_id} set {pair} to {rate}")
            return
        doc_ref = self._get_profile_collection(pair).document(str(profile_id))
        doc_ref.set({"rate": rate})

    def get_profile_rates(self, profile_id: str, pair: str = "GBP-THB") -> float:
        if not IS_PROD:
            logging.info(f"Mocking get_profile_rates: {profile_id} for {pair}")
            return 45.0  # Return a mock rate
        doc_ref = self._get_profile_collection(pair).document(str(profile_id))
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get("rate")
        else:
            return float("inf")

    def get_profile_rates_less_than(self, rate: float, pair: str = "GBP-THB") -> list:
        docs = self._get_profile_collection(pair).where("rate", "<=", rate).stream()
        return [doc.id for doc in docs]

    def get_latest_mvrv_timestamp(self) -> int:
        if not IS_PROD:
            return 0
        doc_ref = self.db.collection("mvrv").document("latest_time")
        doc = doc_ref.get()
        return doc.to_dict().get("timestamp")

    def set_latest_mvrv_timestamp(self, timestamp: int) -> None:
        if not IS_PROD:
            logging.info(f"Mocking set_latest_mvrv_timestamp: {timestamp}")
            return
        doc_ref = self.db.collection("mvrv").document("latest_time")
        doc_ref.set({"timestamp": timestamp})

    def is_for_property_id_pinged(self, id: int) -> bool:
        doc_ref = self.db.collection("for").document(str(id))
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get("pinged")
        return False

    def save_for_property_id(self, id: int) -> None:
        doc_ref = self.db.collection("for").document(str(id))
        doc_ref.set({"pinged": True})
