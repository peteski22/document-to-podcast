import argparse
import json
from pathlib import Path

from loguru import logger
from models import LoadConfig
from preprocessing.data_cleaners import cleaner_by_extension
from preprocessing.data_loaders import data_load
from utils import save_data


def parse_args() -> LoadConfig:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config", type=str, help="Path to the config file or a JSON string, this overrides any other parameters"
    )
    parser.add_argument("--input_file", type=Path, help="Path to the input file")
    parser.add_argument("--output_folder", type=Path, help="Path to the output folder")

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

    return LoadConfig.model_validate(config_data)


def data_clean(input_file: Path, text: str) -> str:
    data_cleaner = cleaner_by_extension(input_file)
    logger.info(f"Cleaning {input_file}")
    clean_data = data_cleaner(text)
    logger.debug(f"Cleaned {len(text) - len(clean_data)} characters")
    logger.debug(f"Length of cleaned text: {len(clean_data)}")
    return clean_data


def load_and_clean_data(input_file: Path) -> str:
    data = data_load(input_file)
    data = data_clean(input_file, data)
    return data


if __name__ == "__main__":
    config = parse_args()
    cleaned_text = load_and_clean_data(config.input_file)
    result_path = save_data(config.output_folder, "cleaned.txt", cleaned_text)
    logger.info(f"Saving cleaned data to {result_path}")
    print(result_path)
