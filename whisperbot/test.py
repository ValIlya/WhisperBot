from whisperbot.chat import Message, Role


print(Message.model_validate(dict(sender=Role.USER, text="test")).model_dump_json())
