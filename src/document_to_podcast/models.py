from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator
from validators import (
    validate_input_file,
    validate_output_folder,
    validate_speakers,
    validate_text_to_speech_model,
    validate_text_to_text_model,
    validate_text_to_text_prompt,
)

_DEFAULT_PROMPT = """
You are a podcast scriptwriter generating engaging and natural-sounding conversations in JSON format.
The script features the following speakers:
{SPEAKERS}
Instructions:
- Write dynamic, easy-to-follow dialogue.
- Include natural interruptions and interjections.
- Avoid repetitive phrasing between speakers.
- Format output as a JSON conversation.
Example:
{
  "Speaker 1": "Welcome to our podcast! Today, we're exploring...",
  "Speaker 2": "Hi! I'm excited to hear about this. Can you explain...",
  "Speaker 1": "Sure! Imagine it like this...",
  "Speaker 2": "Oh, that's cool! But how does..."
}
"""


class Speaker(BaseModel):
    id: int
    name: str
    description: str
    voice_profile: str

    model_config = {
        "frozen": True,
    }

    def __str__(self):
        """Returns a string representation of the speaker."""
        return f"Speaker {self.id}. Named {self.name}. {self.description}"


_DEFAULT_SPEAKERS = frozenset(
    {
        Speaker(
            id=1,
            name="Sarah",
            description="The main host. She explains topics clearly using anecdotes and analogies, "
            "teaching in an engaging and captivating way.",
            voice_profile="af_sarah",
        ),
        Speaker(
            id=2,
            name="Michael",
            description="The co-host. He keeps the conversation on track, asks curious follow-up questions, "
            "and reacts with excitement or confusion, often using interjections like hmm or umm.",
            voice_profile="am_michael",
        ),
    }
)


class InputConfig(BaseModel):
    input_file: Annotated[Path, AfterValidator(validate_input_file)] = Field(
        description="""Path to the input file document on the filesystem.
                    Supported extensions: .docx, .html, .md, .pdf, .txt""",
    )


class OutputConfig(BaseModel):
    output_folder: Annotated[Path, AfterValidator(validate_output_folder)] = Field(
        description="Folder where the output should be saved."
    )


class LoadConfig(InputConfig, OutputConfig):
    pass


class SpeakerConfig(BaseModel):
    speakers: Annotated[list[Speaker], AfterValidator(validate_speakers)] = Field(
        default_factory=lambda: list(_DEFAULT_SPEAKERS), description="List of two speakers to use for the podcast."
    )


class ScriptGenerationConfig(LoadConfig, SpeakerConfig):
    text_to_text_prompt: Annotated[str, AfterValidator(validate_text_to_text_prompt)] = Field(
        default=_DEFAULT_PROMPT, description="System prompt for the script generator."
    )
    text_to_text_model: Annotated[str, AfterValidator(validate_text_to_text_model)] = Field(
        default="bartowski/Qwen2.5-7B-Instruct-GGUF/Qwen2.5-7B-Instruct-Q8_0.gguf",
        description="""Model ID for the script generation step.
                - Needs to be formatted as `owner/repo/file`.
                - Needs to be a gguf file.""",
    )


class AudioGenerationConfig(LoadConfig, SpeakerConfig):
    text_to_speech_model: Annotated[str, AfterValidator(validate_text_to_speech_model)] = Field(
        default="hexgrad/Kokoro-82M", description="Model ID for the text-to-speech engine."
    )
