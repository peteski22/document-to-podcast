import argparse
import json
import re
from pathlib import Path

from prefect import flow, task

import soundfile as sf
from llama_cpp import Llama
from loguru import logger
from numpy import ndarray

from document_to_podcast.config import (
    PodcastConfig,
    Speaker,
)
from document_to_podcast.inference.model_loaders import (
    TTSModel,
    load_llama_cpp_model,
    load_tts_model,
)
from document_to_podcast.inference.text_to_speech import text_to_speech
from document_to_podcast.inference.text_to_text import text_to_text_stream
from document_to_podcast.preprocessing import DATA_CLEANERS, DATA_LOADERS
from document_to_podcast.utils import stack_audio_segments


@task(name="Validate intended output folder")
def ensure_output_folder(output_folder: Path):
    output_folder.mkdir(parents=True, exist_ok=True)


@task(name="Load input data")
def data_load(input_file: Path) -> str:
    data_loader = DATA_LOADERS[input_file.suffix]
    logger.info(f"Loading {input_file}")
    data = data_loader(input_file)
    logger.debug(f"Loaded {len(data)} characters")
    return data


@task(name="Clean input data")
def data_clean(input_file: Path, text: str) -> str:
    data_cleaner = DATA_CLEANERS[Path(input_file).suffix]
    logger.info(f"Cleaning {input_file}")
    clean_data = data_cleaner(text)
    logger.debug(f"Cleaned {len(text) - len(clean_data)} characters")
    logger.debug(f"Length of cleaned text: {len(clean_data)}")
    return clean_data


@task(name="Load text to text model")
def load_text_to_text_model(model: str) -> Llama:
    logger.info(f"Loading text to text model: {model}")
    return load_llama_cpp_model(model_id=model)


@task(name="Load text to speech model")
def load_text_to_speech_model(model: str, speakers: list[Speaker]) -> TTSModel:
    logger.info(f"Loading text to speech model: {model}")
    return load_tts_model(
        model_id=model,
        **{"lang_code": speakers[0].voice_profile[0]},
    )


#@cf.task()
@task(name="Limit input text size")
def limit_text_size(text: str, text_model: Llama) -> str:
    # ~4 characters per token is considered a reasonable default.
    max_characters = text_model.n_ctx() * 4
    if len(text) <= max_characters:
        return text

    logger.warning(f"Input text is too big ({len(text)}). Using a subset of ({max_characters}) characters.")
    return text[:max_characters]


@task(name="Save podcast script")
def save_podcast_script(output_folder: Path, podcast_script: str):
    logger.info("Saving Podcast script...")
    output_folder.write_text(podcast_script)


@task(name="Save podcast audio")
def save_podcast_audio(output_folder: Path, complete_audio: ndarray, sample_rate: int):
    logger.info("Saving Podcast audio...")
    sf.write(str(output_folder), complete_audio, samplerate=sample_rate)


@task(name="Prepare Podcast data and settings")
def prepare(config: PodcastConfig) -> (str, Llama, TTSModel):
    ensure_output_folder(config.output_folder)
    text = data_load(config.input_file)
    cleaned_text = data_clean(config.input_file, text)
    text_model = load_text_to_text_model(config.text_to_text_model)
    speech_model = load_text_to_speech_model(config.text_to_speech_model, config.speakers)
    cleaned_text = limit_text_size(cleaned_text, text_model)
    return cleaned_text, text_model, speech_model


@task(name="Generate podcast")
def generate(config: PodcastConfig, input_text: str, text_model: Llama, speech_model: TTSModel) -> (ndarray, str):
    logger.info("Generating Podcast...")
    podcast_script = ""
    text = ""
    podcast_audio = []
    system_prompt = config.text_to_text_prompt.strip()
    system_prompt = system_prompt.replace("{SPEAKERS}", "\n".join(str(speaker) for speaker in config.speakers))

    for chunk in text_to_text_stream(input_text, text_model, system_prompt=system_prompt):
        text += chunk
        podcast_script += chunk
        if text.endswith("\n") and "Speaker" in text:
            logger.debug(text)
            speaker_id = re.search(r"Speaker (\d+)", text).group(1)
            voice_profile = next(speaker.voice_profile for speaker in config.speakers if speaker.id == int(speaker_id))
            speech = text_to_speech(
                text.split(f'"Speaker {speaker_id}":')[-1],
                speech_model,
                voice_profile,
            )
            podcast_audio.append(speech)
            text = ""

    logger.info("Compiling Podcast...")
    complete_audio = stack_audio_segments(podcast_audio, sample_rate=speech_model.sample_rate, silence_pad=1.0)
    return complete_audio, podcast_script


@task(name="Store Podcast")
def store(output_folder: Path, complete_audio: ndarray, sample_rate: int, podcast_script: str):
    logger.info("Saving Podcast...")
    save_podcast_script(output_folder / "podcast.txt", podcast_script)
    save_podcast_audio(output_folder / "podcast.wav", complete_audio, sample_rate)


@logger.catch(reraise=True)
@flow(name="Document to Podcast")
def document_to_podcast(config: PodcastConfig):
    """Generate a podcast from a document.

    Args:
        config (PodcastConfig): The configuration for the podcast generation.
    """
    cleaned_text, text_model, speech_model = prepare(config)
    podcast_audio, podcast_script = generate(config, cleaned_text, text_model, speech_model)
    store(config.output_folder, podcast_audio, speech_model.sample_rate, podcast_script)
    logger.info("Podcast generation complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a document to a podcast.")

    # Add argument for JSON configuration input
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="JSON string or path to the JSON configuration file")

    args = parser.parse_args()

    # Parse the config argument: if it's a path, load the JSON file
    if Path(args.config).exists():
        with Path.open(args.config, "r") as f:
            config_data = json.load(f)
    else:
        # If it's not a file, treat it as a JSON string
        config_data = json.loads(args.config)

    # Create the Pydantic model from the dictionary
    #podcast_config = PodcastConfig.model_validate(config_data)
    document_to_podcast(config_data)