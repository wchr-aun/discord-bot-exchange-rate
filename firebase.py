from firebase_admin import credentials, firestore, initialize_app
import json


class Firebase:
    def __init__(self, service_account: str) -> None:
        SERVICE_ACCOUNT = service_account
        cred = credentials.Certificate(json.loads(SERVICE_ACCOUNT))
        initialize_app(cred)
        self.db = firestore.client()

    def set_profile_rates(self, profile_id: str, rate: float) -> None:
        doc_ref = self.db.collection(u'profiles').document(str(profile_id))
        doc_ref.set({ 'rate': rate })

    def get_profile_rates(self, profile_id: str) -> float:
        doc_ref = self.db.collection(u'profiles').document(str(profile_id))
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get('rate')
        else:
            return float('inf')
        
    def get_profile_rates_less_than(self, rate: float) -> list:
        docs = self.db.collection(u'profiles').where(u'rate', u'<=', rate).stream()
        return [doc.id for doc in docs]
