from __future__ import annotations

from email.header import decode_header
from email.message import Message


def decode_text(text: str | None) -> str:
    if text is None:
        return ""

    decoded_parts = decode_header(text)
    result = ""

    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result += part.decode(encoding or "utf-8", errors="ignore")
        else:
            result += part

    return result


def get_body(msg: Message) -> str:
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    body += payload.decode(
                        part.get_content_charset() or "utf-8",
                        errors="ignore",
                    )
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(
                msg.get_content_charset() or "utf-8",
                errors="ignore",
            )

    return body


def has_attachment(msg: Message) -> str:
    for part in msg.walk():
        if part.get_filename():
            return "Y"
    return "N"

