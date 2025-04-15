import argparse
import json
import re
from pathlib import Path

import soundfile as sf
from inference.text_to_speech import text_to_speech
from loguru import logger
from models import AudioGenerationConfig, Speaker
from numpy import ndarray
from preprocessing.data_loaders import data_load
from preprocessing.model_loaders import TTSModel, tts_loader_by_model
from utils import stack_audio_segments


def parse_args() -> AudioGenerationConfig:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", type=str, help="Path to the config file or a JSON string, this overrides any other parameters"
    )
    parser.add_argument("--input_file", type=Path)
    parser.add_argument("--output_folder", type=Path)
    parser.add_argument("--text_to_speech_model", type=str)
    parser.add_argument("--speakers", type=list[Speaker], help="JSON string defining speakers")

    args = parser.parse_args()

    config_data = {}

    if args.config:
        if Path(args.config).exists():
            with Path.open(args.config, "r") as f:
                config_data = json.load(f)
        else:
            config_data = json.loads(args.config)
    else:
        config_data = vars(args)

    config_data = {k: v for k, v in vars(args).items() if v is not None}

    return AudioGenerationConfig.model_validate(config_data)


def load_text_to_speech_model(model: str, lang_code: str = "b") -> TTSModel:
    logger.info(f"Loading text to speech model: {model}, with lang code: {lang_code}")
    return tts_loader_by_model(model)(
        model_id=model,
        **{"lang_code": lang_code},
    )


def generate_audio(input_script: str, speech_model: TTSModel, speakers: list[Speaker]) -> ndarray:
    logger.info("Generating podcast audio...")

    podcast_audio = []

    for line in input_script.split("\n"):
        if "Speaker" not in line:
            continue
        logger.debug(line)
        speaker_id = re.search(r"Speaker (\d+)", line).group(1)
        voice_profile = next(speaker.voice_profile for speaker in speakers if speaker.id == int(speaker_id))
        speech = text_to_speech(
            line.split(f'"Speaker {speaker_id}":')[-1],
            speech_model,
            voice_profile,
        )
        podcast_audio.append(speech)

    complete_audio = stack_audio_segments(podcast_audio, sample_rate=speech_model.sample_rate, silence_pad=1.0)

    return complete_audio


def save_podcast_audio(output_folder: Path, filename: str, complete_audio: ndarray, sample_rate: int):
    output_path = output_folder / filename
    logger.info(f"Saving Podcast audio to {output_path}")
    sf.write(str(output_path), complete_audio, samplerate=sample_rate)
    return str(output_path)


def do_audio_generation(script: str, model_id: str, speakers: list[Speaker]) -> (ndarray, int):
    lang_code = speakers[0].voice_profile[0]
    text_to_speech_model = load_text_to_speech_model(model_id, lang_code)
    audio = generate_audio(script, text_to_speech_model, speakers)
    return audio, text_to_speech_model.sample_rate


if __name__ == "__main__":
    config = parse_args()
    text = data_load(config.input_file)
    podcast_audio: ndarray
    sample_rate: int
    podcast_audio, sample_rate = do_audio_generation(text, config.text_to_speech_model, config.speakers)
    result_path = save_podcast_audio(config.output_folder, "podcast.wav", podcast_audio, sample_rate)
    print(result_path)
