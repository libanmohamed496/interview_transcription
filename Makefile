.PHONY: pyannote_venv openai_venv

pyannote_venv:
	python3 -m venv .venv_pyannote
	@. .venv_pyannote/bin/activate; \
	pip install -r requirements_pyannote.txt; \
	deactivate;
	@echo ".venv_pyannote environment setup complete."

openai_venv:
	python3 -m venv .venv_openai
	@. .venv_openai/bin/activate; \
	pip install -r requirements_openai.txt; \
	deactivate;
	@echo ".venv_openai environment setup complete."

RAW_DIR = data/raw
INTERMEDIATE_DIR = data/intermediate
OUTPUT_DIR = data/output

$(INTERMEDIATE_DIR)/%.rttm: $(RAW_DIR)/%.mp3
	@echo "`date '+%Y-%m-%d %H:%M:%S'`: Generating rttm for $<..."
	.venv_pyannote/bin/python diarization.py --filepath $<

$(OUTPUT_DIR)/%.txt: $(RAW_DIR)/%.mp3 $(INTERMEDIATE_DIR)/%.rttm
	@echo "`date '+%Y-%m-%d %H:%M:%S'`: Generating transcript for $<..."
	.venv_openai/bin/python transcription.py --filepath $<

MP3_FILES = $(wildcard $(RAW_DIR)/*.mp3)
RTTM_FILES = $(patsubst $(RAW_DIR)/%.mp3,$(INTERMEDIATE_DIR)/%.rttm,$(MP3_FILES))
TXT_FILES = $(patsubst $(RAW_DIR)/%.mp3,$(OUTPUT_DIR)/%.txt,$(MP3_FILES))

all: $(RTTM_FILES) $(TXT_FILES)

