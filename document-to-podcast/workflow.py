from flytekit import workflow, FlyteFile
from tasks.downloader import download_document
from tasks.transformer import transform_document
from tasks.scriptwriter import scriptwriter
from tasks.performer import performer


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
    downloaded = download_document(url=document_url)

    transformed = transform_document(
        html_file=downloaded.html_file,
        file_type=file_type
    )

    script = scriptwriter(
        processed_document=transformed.processed_document,
        host_name=host_name,
        cohost_name=cohost_name
    )

    audio = performer(
        podcast_script=script.podcast_script,
        host_voice_profile=host_voice_profile,
        cohost_voice_profile=cohost_voice_profile,
        file_type=audio_format
    )

    return audio.podcast
