## About

This project produces interview transcripts from `.mp3` files. Timestamps corresponding to the onset of each speaker are produced in `interview_transcription/diarize.py`; these are used to annotate a transcription produced in `interview_transcription/transcribe.py`.

Speaker diarization uses Pyannote Speaker Diarization 3.1, which is slow but adequate at assigning speaker. Transcription uses OpenAI Whisper 1, which works well for my data and is cost-effective at <$1 per hour of audio.

## Setup

You'll need python3, ffmpeg, and OpenAI and HuggingFace API keys. Place the API keys in `.env`, following `.env.example`. Go to the diarization model [page](https://huggingface.co/pyannote/speaker-diarization-3.1) and fill the form for access. On Mac, run
```
brew install ffmpeg
```

Dependencies clash between two tools, so we use two environments.

```
make pyannote_venv
make openai_venv
```

## Interview transcription

To use, put `.mp3` files in `data/raw/`, then run the `make` command:
```
make all
```

There are also `make` commands for each individual step; see the `Makefile`
