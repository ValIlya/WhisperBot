from typing import List
from pymongo import MongoClient
from whisperbot.models import Message, MessageCollection


class Storage:
    def __init__(self, connstring: str, database: str, collection: str) -> None:
        client = MongoClient(connstring)
        db = client[database]
        self.collection = db[collection]

    def save_new_dialogue(self, chat_id):
        self.collection.insert_one(
            {
                "chat_id": chat_id,
                "messages": [],
            }
        )

    def append_message(self, chat_id: int, message: Message):
        self.collection.update_one(
            {"chat_id": chat_id},
            {
                "$push": {
                    "messages": message.model_dump(),
                }
            },
            upsert=True,
        )

    def get_messages(self, chat_id: int, n: int = 0) -> List[Message]:
        query = [{"chat_id": chat_id}]
        if n > 0:
            query.append({"messages": {"$slice": -n}})
        chat = self.collection.find_one(*query)

        if chat:
            return MessageCollection.model_validate(chat).messages
        else:
            return []

    def delete_chat_history(self, chat_id: int):
        self.collection.delete_one({"chat_id": chat_id})
