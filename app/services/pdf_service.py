from __future__ import annotations

from email.header import decode_header
from email.message import Message
from pathlib import Path

import pandas as pd
import pdfplumber


def download_pdf_attachment(msg: Message, download_dir: Path) -> Path | None:
    for part in msg.walk():
        content_disposition = part.get("Content-Disposition")
        if not content_disposition or "attachment" not in content_disposition:
            continue

        filename = part.get_filename()
        if not filename:
            continue

        decoded_filename, encoding = decode_header(filename)[0]
        if isinstance(decoded_filename, bytes):
            decoded_filename = decoded_filename.decode(encoding or "utf-8", errors="replace")

        if not decoded_filename.lower().endswith(".pdf"):
            continue

        filepath = download_dir / decoded_filename
        with filepath.open("wb") as file_obj:
            file_obj.write(part.get_payload(decode=True))
        return filepath

    return None


def pdfs_to_df(pdf_files: list[str]) -> pd.DataFrame:
    rows: list[dict[str, str]] = []

    for pdf_path in pdf_files:
        full_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

        rows.append({"title": Path(pdf_path).name, "content": full_text.strip()})

    return pd.DataFrame(rows)


def add_nouns_column(df: pd.DataFrame) -> pd.DataFrame:
    from konlpy.tag import Komoran

    komoran = Komoran()
    result_df = df.copy()
    result_df["nouns"] = result_df["content"].apply(
        lambda value: [noun for noun in komoran.nouns(value) if len(noun) >= 2]
    )
    return result_df


def add_document_column(df: pd.DataFrame) -> pd.DataFrame:
    result_df = df.copy()
    result_df["document"] = result_df["nouns"].apply(lambda nouns: " ".join(nouns))
    return result_df

