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

### TODO:
 - markdown support for answers
   - strip unsupported characters
 - don't save audio to disk
 - async 
    - read-write to storage (Motor)
    - llm chat
 - suggests for bot commands
 - tests would be nice
   - how to test telegram api?
