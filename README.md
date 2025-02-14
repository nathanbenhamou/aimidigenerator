# aimidigenerator
This is an experiment to generate midi notes with GPT-4o.

The output is generated in JSON which it then converted into a midi file with Pretty midi. The midi player is provided by html-midi-player.You can find the whole project including the next features on Github. Please reach out if you have feedback or if you want to contribute.

Works with FastAPI.

To launch,run
```
uvicorn server:app --reload
```

You need an OpenAI key exported as an environment variable. More info: https://platform.openai.com/docs/quickstart

Next up:
- Improve the prompt
- Drag and drop existing midifile to use as a basis to ask the LLM to modify or extend them
