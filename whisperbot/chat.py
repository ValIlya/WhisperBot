from typing import List
from mistralai import Mistral
from whisperbot.models import Message


class Role:
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Chat:
    def __init__(self, token: str) -> None:
        self.client = Mistral(api_key=token)
        self.model = "mistral-small-latest"

    def get_model_list(self) -> List[str]:
        models = []
        response = self.client.models.list()
        for card in response.data:
            if card.capabilities.completion_chat:
                models.append(card.id)
        return models

    def _format(self, m: Message) -> dict:
        return {
            "role": m.sender,
            "content": m.text,
        }

    def reply(self, messages: List[Message] = []) -> str:
        raw_messages = []
        assert len(messages) > 0
        for message in messages:
            raw_messages.append(self._format(message))

        chat_response = self.client.chat.complete(
            model=self.model,
            messages=raw_messages,
        )
        return chat_response.choices[0].message.content
