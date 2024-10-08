import datetime
from typing import List

from pydantic import BaseModel, Field


class Message(BaseModel, extra="allow"):
    sender: str
    text: str
    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    deleted: bool = False


class UserData(BaseModel, extra="allow"):
    chat_id: int
    messages: List[Message] = []
    language: str = "auto"
