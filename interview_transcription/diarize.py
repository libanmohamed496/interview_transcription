import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from pyannote.audio import Pipeline


def parse_args():
    parser = argparse.ArgumentParser(description="Process a filepath.")
    parser.add_argument(
        "--filepath",
        type=str,
        required=True,
        help="The path to the file you want to process",
    )
    args = parser.parse_args()
    return args


def main(args):
    load_dotenv()

    file_path = Path(args.filepath)
    out_dir = Path("data/intermediate")
    out_path = out_dir / (file_path.stem + ".rttm")

    out_dir.mkdir(parents=True, exist_ok=True)

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1", use_auth_token=os.environ["HF_ACCESS_TOKEN"]
    )

    diarization = pipeline(args.filepath)

    with open(out_path, "w") as rttm:
        diarization.write_rttm(rttm)


if __name__ == "__main__":
    args = parse_args()
    main(args)
