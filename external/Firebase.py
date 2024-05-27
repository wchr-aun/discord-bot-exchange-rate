import json

from firebase_admin import credentials, firestore, initialize_app


class Firebase:
    def __init__(self, service_account: str) -> None:
        SERVICE_ACCOUNT = service_account
        cred = credentials.Certificate(json.loads(SERVICE_ACCOUNT))
        initialize_app(cred)
        self.db = firestore.client()

    def set_profile_rates(self, profile_id: str, rate: float) -> None:
        doc_ref = self.db.collection("profiles").document(str(profile_id))
        doc_ref.set({"rate": rate})

    def get_profile_rates(self, profile_id: str) -> float:
        doc_ref = self.db.collection("profiles").document(str(profile_id))
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get("rate")
        else:
            return float("inf")

    def get_profile_rates_less_than(self, rate: float) -> list:
        docs = self.db.collection("profiles").where("rate", "<=", rate).stream()
        return [doc.id for doc in docs]

    def get_latest_mvrv_timestamp(self) -> int:
        doc_ref = self.db.collection("mvrv").document("latest_time")
        doc = doc_ref.get()
        return doc.to_dict().get("timestamp")

    def set_latest_mvrv_timestamp(self, timestamp: int) -> None:
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
