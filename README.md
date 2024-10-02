# WhisperBot

Bot for chatting with LLM

- Install ffmpeg `apt install ffmpeg`
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
 - async 
    - read-write to storage (Motor)
    - llm chat
 - tests would be nice
   - how to test telegram api?
