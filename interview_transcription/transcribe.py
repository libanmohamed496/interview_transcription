import argparse
import asyncio
import os
from collections import deque
from math import isnan
from pathlib import Path
from time import sleep, time

import openai
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment


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


def get_rttf(filepath):
    columns = [
        "type",
        "file_id",
        "channel_id",
        "start_time",
        "duration",
        "orthography",
        "speaker_type",
        "speaker_id",
        "confidence",
        "slt",
    ]

    df = pd.read_csv(filepath, sep=" ", names=columns)
    df["speaker_change"] = df["speaker_id"] != df["speaker_id"].shift(1)
    return df


def _query_whisper(client, audio, j, start_time, end_time, speaker_id):
    if isnan(end_time):
        segment = audio[int(start_time * 1000) :]
    else:
        segment = audio[int(start_time * 1000) : int(end_time * 1000)]
    if len(segment) < 500:
        return (start_time, "", "")
    temp_path = Path("data/intermediate/") / f"segment_{start_time}.mp3"
    segment.export(temp_path, format="mp3")

    # TODO: error handling, retries
    # retries = 5
    # wait_0 = 1
    # r = 2
    # wait = wait_0
    with open(temp_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, language="en"
        )
        transcript = (start_time, speaker_id, response.text)
    # if response.status_code == 429:
    #     error_details = response.json()
    #     print(f"Rate limit reached: {error_details['error']['message']}")
    #     print(f"Retrying in {wait}s")
    #     sleep(wait)
    #     wait *= r
    #     retries -= 1

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return transcript


async def query_whisper(client, audio, change_df, rpm_limit=50, batch_size=5):
    args_list = []
    for j, (start_time, end_time, speaker_id) in enumerate(
        zip(
            change_df["start_time"],
            change_df["start_time"].shift(-1),
            change_df["speaker_id"],
        )
    ):
        args_list.append((client, audio, j, start_time, end_time, speaker_id))
    tasks = [asyncio.to_thread(_query_whisper, *args) for args in args_list]

    transcripts = []
    call_times = deque()
    for j in range(0, len(tasks), batch_size):
        curr_time = time()
        call_times.append(curr_time)
        while len(call_times) > rpm_limit // batch_size:
            call_times.popleft()
        sleep(min(60 - (call_times[-1] - call_times[0]) + 1, 1))

        try:
            transcripts_ = await asyncio.gather(*tasks[j : j + batch_size])
            sleep(1)
        except Exception as e:
            print(e)
            print(tasks[j : j + batch_size])
        transcripts.extend(transcripts_)

    return transcripts


def main(args):
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI()

    file_path = Path(args.filepath)
    intermediate_dir = Path("data/intermediate")
    out_dir = Path("data/output")
    output_path = out_dir / (file_path.stem + ".txt")

    intermediate_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    audio = AudioSegment.from_mp3(file_path)

    rttf_df = get_rttf(intermediate_dir / (file_path.stem + ".rttm"))
    change_df = rttf_df[rttf_df["speaker_change"]]

    transcripts = asyncio.run(query_whisper(client, audio, change_df))
    transcripts.sort()

    with open(output_path, "w") as f:
        for t, speaker, text in transcripts:
            m = str(t // (60))
            ss = "{:.2f}".format(t % 60)
            f.write(f"({m}:{ss}) -- {speaker}:\n")
            f.write(f"{text}\n\n")


if __name__ == "__main__":
    args = parse_args()
    main(args)
