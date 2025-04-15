from collections.abc import Callable
from pathlib import Path
from typing import TypeAlias

import PyPDF2
import requests
from docx import Document
from loguru import logger
from streamlit.runtime.uploaded_file_manager import UploadedFile

TextLoaderFn: TypeAlias = Callable[[Path | UploadedFile | str], str | None]


def load_pdf(pdf_file: str | UploadedFile) -> str | None:
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        return "\n".join(page.extract_text() for page in pdf_reader.pages)
    except Exception as e:
        logger.exception(e)
        return None


def load_txt(txt_file: Path | UploadedFile) -> str | None:
    try:
        if isinstance(txt_file, UploadedFile):
            return txt_file.getvalue().decode("utf-8")
        else:
            with Path.open(txt_file) as file:
                return file.read()
    except Exception as e:
        logger.exception(e)
        return None


def load_docx(docx_file: str | UploadedFile) -> str | None:
    try:
        docx_reader = Document(docx_file)
        return "\n".join(paragraph.text for paragraph in docx_reader.paragraphs)
    except Exception as e:
        logger.exception(e)
        return None


def load_url(url: str) -> str | None:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.exception(e)
        return None


def loader_by_extension(path: Path) -> TextLoaderFn:
    ext = Path(path).suffix.lower()
    match ext:
        case ".txt" | ".md" | ".html":
            return load_txt
        case ".pdf":
            return load_pdf
        case ".docx":
            return load_docx
        case "url":
            return load_url
        case _:
            raise ValueError(f"Unsupported extension: {ext}")


def data_load(input_file: Path) -> str:
    data_loader = loader_by_extension(input_file)
    logger.info(f"Loading {input_file}")
    data = data_loader(input_file)
    if not data:
        raise ValueError("No data loaded")
    return data
