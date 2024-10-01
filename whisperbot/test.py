from whisperbot.speech2text import Speech2Text

model = Speech2Text()
stream = open(
    "AwACAgIAAxkBAANeZvu9GYtra0kinkq2lHjuE-g_lA4AAhhjAAJ1CthLgqgSb9GZfzg2BA.ogg", "rb"
)
text = model.transcribe_stream(stream)
print(text)
