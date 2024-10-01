from whisperbot.speech2text import Speech2Text

model = Speech2Text()
print(model.get_available_languages())
text = model.transcribe(
    "whisperbot/AwACAgIAAxkBAAMnZvscDx2J_RR4adQehjte7iApAAH1AAKbVgACTdrgS8wZHJCc9PEkNgQ.ogg"
)
print(text)
