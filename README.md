# README

## Requirements

* [UV](https://docs.astral.sh/uv/getting-started/installation/) (can be installed via `curl -LsSf https://astral.sh/uv/install.sh | sh`)
* Internet access to download any models (including during runtime)

## Setup

* Clone the repo
* `uv venv --python 3.11 && source .venv/bin/activate`
* `uv sync`

## Running the workflow steps

The steps can be run from within the repo root directory, each step requires the output from the previous step.

Some steps have optional parameters, which will use sensible defaults.

### Loading and cleaning data

```bash
uv run python src/document_to_podcast/load_data.py \
--input_file "$(pwd)/example_data/Mozilla-Trustworthy_AI.md" \
--output_folder "$(pwd)output"
```

### Generating the podcast script

```bash
uv run python src/document_to_podcast/generate_script.py \
--input_file "$(pwd)/output/cleaned.txt" \
--output_folder "$(pwd)/output"
```

### Generating the podcast audio

```bash
uv run python src/document_to_podcast/generate_audio.py \
--input_file "$(pwd)/output/podcast.txt" \
--output_folder "$(pwd)/output"
```

## Notes

You can also supply config as a path to a file containing JSON, or as a JSON string.

For example, running the `load_data` script and supplying the `--config` flag with the following JSON:

```json
{
  "input_file": "/Users/foo/src/document-to-podcast/example_data/Mozilla-Trustworthy_AI.md",
  "output_folder": "/Users/foo/src/document-to-podcast/output"
}
```

```bash
uv run python src/document_to_podcast/load_data.py \
--config '{"input_file": "/Users/foo/src/document-to-podcast/example_data/Mozilla-Trustworthy_AI.md", "output_folder": "/Users/foo/src/document-to-podcast/output"}'
```

or if the JSON is stored in a file at `/Users/foo/src/document-to-podcast/my_config.json`:

```bash
uv run python src/document_to_podcast/load_data.py \
--config "/Users/foo/src/document-to-podcast/my_config.json"
```
