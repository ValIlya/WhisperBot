from typing import List

from pymongo import MongoClient

from whisperbot.models import Message, UserData


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

    def get_messages(self, chat_id: int) -> List[Message]:
        chat = self.collection.find_one(
            {"chat_id": chat_id},
            {
                "chat_id": True,
                "messages": {
                    "$elemMatch": {"deleted": False},
                },
            },
        )

        if chat:
            return UserData.model_validate(chat).messages
        else:
            return []

    def delete_chat_history(self, chat_id: int):
        self.collection.update_many(
            {"chat_id": chat_id}, {"$set": {"messages.$[].deleted": True}}
        )

    def set_language(self, chat_id: int, language: str):
        self.collection.update_many(
            {"chat_id": chat_id}, {"$set": {"language": language}}
        )

    def get_language(self, chat_id: int) -> str:
        data = self.collection.find_one(
            {"chat_id": chat_id}, {"chat_id": True, "language": True}
        )
        if data:
            return UserData.model_validate(data).language
        else:
            return UserData(chat_id=chat_id).language
