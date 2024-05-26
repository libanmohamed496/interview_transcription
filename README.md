You'll need python3, ffmpeg, and OpenAI and HuggingFace API keys. Place the API keys in `.env`, following `.env.example`. Go to the diarization model [page](https://huggingface.co/pyannote/speaker-diarization-3.1) and fill the form for access. Run
```
brew install ffmpeg
```

Dependencies clash between two tools, so we use two environments.

```
make pyannote_venv
make openai_venv
```

To use, put `.mp3` files in `data/raw/`, then run the `make` command:
```
make all
```

There are also `make` commands for each individual step; see the `Makefile`