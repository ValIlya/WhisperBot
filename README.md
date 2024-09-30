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
 - support audio parsing
 - mark messages as deleted, but not delete
 - markdown support for answers
 - async 
    - read-write to storage (Motor)
    - llm chat
 - suggests for bot commands
 - tests would be nice
   - how to test telegram api?
