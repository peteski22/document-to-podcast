import argparse
import json
from pathlib import Path

from inference.text_to_text import text_to_text_stream
from llama_cpp import Llama
from loguru import logger
from models import ScriptGenerationConfig, Speaker
from preprocessing.data_loaders import data_load
from preprocessing.model_loaders import load_llama_cpp_model
from utils import save_data


def parse_args() -> ScriptGenerationConfig:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config", type=str, help="Path to the config file or a JSON string, this overrides any other parameters"
    )
    parser.add_argument("--input_file", type=Path, help="Path to the input file")
    parser.add_argument("--output_folder", type=Path, help="Path to the output folder")
    parser.add_argument("--text_to_text_prompt", type=str)
    parser.add_argument("--text_to_text_model", type=str)
    parser.add_argument("--speakers", type=list[Speaker], help="Path to JSON file defining speakers")

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

    return ScriptGenerationConfig.model_validate(config_data)


def load_text_to_text_model(model: str) -> Llama:
    logger.info(f"Loading text to text model: {model}")
    return load_llama_cpp_model(model_id=model)


def limit_text_size(cleaned_text: str, text_model: Llama) -> str:
    # ~4 characters per token is considered a reasonable default.
    max_characters = text_model.n_ctx() * 4
    if len(cleaned_text) <= max_characters:
        return cleaned_text

    logger.warning(f"Input text is too big ({len(cleaned_text)}). Using a subset of ({max_characters}) characters.")
    return cleaned_text[:max_characters]


def generate_script(input_text: str, text_model: Llama, system_prompt: str, speakers: list[Speaker]) -> str:
    logger.info("Generating podcast script...")

    system_prompt = system_prompt.strip().replace("{SPEAKERS}", "\n".join(str(speaker) for speaker in speakers))
    podcast_script = ""

    for chunk in text_to_text_stream(input_text, text_model, system_prompt=system_prompt):
        podcast_script += chunk

    return podcast_script


def do_script_generation(text: str, model_id: str, system_prompt: str, speakers: list[Speaker]) -> str:
    text_to_text_model = load_text_to_text_model(model_id)
    text = limit_text_size(text, text_to_text_model)
    return generate_script(text, text_to_text_model, system_prompt, speakers)


if __name__ == "__main__":
    config = parse_args()
    text = data_load(config.input_file)
    script = do_script_generation(text, config.text_to_text_model, config.text_to_text_prompt, config.speakers)
    result_path = save_data(config.output_folder, "podcast.txt", script)
    logger.info(f"Saved generated script to {result_path}")
    print(result_path)
