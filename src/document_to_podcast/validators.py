from inference.text_to_speech import get_text_to_speech_generator
from preprocessing.data_loaders import loader_by_extension
from preprocessing.model_loaders import tts_loader_by_model


def validate_input_file(value):
    loader_by_extension(value)
    return value


def validate_output_folder(value):
    value.mkdir(parents=True, exist_ok=True)
    return value


def validate_text_to_text_model(value):
    parts = value.split("/", maxsplit=3)
    if len(parts) != 3:
        raise ValueError("text_to_text_model must be formatted as `owner/repo/file`")
    if not value.endswith(".gguf"):
        raise ValueError("text_to_text_model must be a gguf file")
    return value


def validate_text_to_text_prompt(value):
    if "{SPEAKERS}" not in value:
        raise ValueError("text_to_text_prompt must contain `{SPEAKERS}` placeholder")
    return value


def validate_text_to_speech_model(value):
    if not tts_loader_by_model(value):
        raise ValueError(
            f"Model {value} is missing a loading function. Please define it under loaders/model_loaders.py"
        )
    if not get_text_to_speech_generator(value):
        raise ValueError(
            f"Model {value} is missing a inference function. Please define it under inference/text_to_speech.py"
        )
    return value


def validate_speakers(value):
    if len(value) != 2:
        raise ValueError("Exactly two speakers are required")
    if value[0].voice_profile[0] != value[1].voice_profile[0]:
        raise ValueError(
            "Both speakers need to have the same language code. "
            "More info here https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md"
        )
    return value
