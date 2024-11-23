# WhisperBot

Bot for chatting with LLM

- Install ffmpeg `apt install ffmpeg`
- Start mongoDB (`mongod` or in a [cloud](https://www.mongodb.com/cloud/atlas))
- Install python dependencies `poetry install`
- Create dotenv `.env` file, see [env.template](env.template) `cp env.template .env`
- Run bot via `startbot`


### Development
Tests
```bash
pytest tests
```
Linter
```bash
cat << EOF >> .git/hooks/pre-commit
ruff check --select I --fix
ruff format
EOF
```

### TODO:
 - mp3 / youtube video transcription / summarization
   - yt dlp subtitles
 - fix chainging language: save/load audio, transcript audio from storage
 - show processing status
 - multi-voice audio, detect speakers
 - multi-language audio
 - async
    - read-write to storage (Motor)
    - llm chat
 - tests would be nice
   - how to test telegram api?
