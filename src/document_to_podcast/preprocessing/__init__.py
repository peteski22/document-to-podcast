from types import MappingProxyType

from .data_cleaners import clean_html, clean_markdown, clean_with_regex
from .data_loaders import load_docx, load_pdf, load_txt, load_url

DATA_LOADERS = MappingProxyType(
    {
        ".docx": load_docx,
        ".html": load_txt,
        ".md": load_txt,
        ".pdf": load_pdf,
        ".txt": load_txt,
        "url": load_url,
    }
)

DATA_CLEANERS = MappingProxyType(
    {
        ".docx": clean_with_regex,
        ".html": clean_html,
        ".md": clean_markdown,
        ".pdf": clean_with_regex,
        ".txt": clean_with_regex,
    }
)
