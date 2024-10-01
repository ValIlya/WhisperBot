# WhisperBot

Bot for chatting with LLM

```bash
cp env.template .env
poetry install
```
Fill up env variables  
Run bot via
```bash
startbot
```


### Development
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
