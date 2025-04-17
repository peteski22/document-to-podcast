from flytekit import workflow, FlyteFile, task

from tasks.downloader import download_document
from tasks.transformer import transform_document
from tasks.scriptwriter import scriptwriter
from tasks.performer import performer


@task
def download_document_task(url: str) -> FlyteFile:
    return download_document(url=url).downloaded_file


@task
def transform_document_task(file: FlyteFile, file_type: str) -> FlyteFile:
    return transform_document(file=file, file_type=file_type).processed_document


@task
def write_script_task(file: FlyteFile, host_name: str, cohost_name: str) -> FlyteFile:
    return scriptwriter(
        processed_document=file,
        host_name=host_name,
        cohost_name=cohost_name
    ).podcast_script


@task
def generate_podcast_audio_task(
        podcast_script: FlyteFile,
        host_voice_profile: str,
        cohost_voice_profile: str,
        audio_format: str) -> FlyteFile:
    return performer(
        podcast_script=podcast_script,
        host_voice_profile=host_voice_profile,
        cohost_voice_profile=cohost_voice_profile,
        file_type=audio_format
    ).podcast


@workflow
def document_to_podcast(
    document_url: str,
    file_type: str = ".html",
    audio_format: str = "WAV",
    host_name: str = "Sarah",
    cohost_name: str = "Michael",
    host_voice_profile: str = "af_sarah",
    cohost_voice_profile: str = "am_michael"
) -> FlyteFile:
    downloaded_file = download_document_task(url=document_url)
    processed_document = transform_document_task(file=downloaded_file, file_type=file_type)
    podcast_script = write_script_task(processed_document, host_name=host_name, cohost_name=cohost_name)
    podcast_audio = generate_podcast_audio_task(podcast_script, host_voice_profile, cohost_voice_profile, audio_format)

    return podcast_audio
