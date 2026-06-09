import io

from pypdf import PdfReader


def extract_text_from_pdf(file_storage) -> str:
    """Extract plain text from an uploaded PDF file."""
    file_bytes = file_storage.read()
    file_storage.seek(0)

    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text.strip())

    return "\n\n".join(text_parts).strip()
