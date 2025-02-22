# chat_service.py

class ChatService:
    def __init__(self, memobase_client):
        self.memobase_client = memobase_client

    def process_chat_message(self, user_id, message):
        blob_id = self.memobase_client.store_blob(user_id, message)
        return blob_id

    def get_chat_history(self, user_id, page, page_size):
        chat_history = self.memobase_client.retrieve_blobs(user_id, page, page_size)
        return chat_history
