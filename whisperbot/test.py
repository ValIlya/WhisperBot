from whisperbot.speech2text import Speech2Text

model = Speech2Text()
text = model.transcribe(
    "whisperbot/AwACAgIAAxkBAAMnZvscDx2J_RR4adQehjte7iApAAH1AAKbVgACTdrgS8wZHJCc9PEkNgQ.wav"
)
print(text)
