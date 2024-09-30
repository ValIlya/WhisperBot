from whisper_cpp_python import Whisper

whisper = Whisper(model_path="./models/ggml-base.en.bin")

output = whisper.transcribe(open("samples/jfk.wav"))

print(output)
