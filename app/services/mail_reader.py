from __future__ import annotations

import email
import imaplib

import pandas as pd

from app.config import AppConfig
from app.models.schemas import MailRecord, PdfAttachment
from app.services.mail_classifier import (
    analyze_priority_deadline,
    classify_mail,
    get_status,
)
from app.services.mail_parser import decode_text, get_body, has_attachment
from app.services.pdf_service import download_pdf_attachment


def load_recent_emails(config: AppConfig, count: int) -> tuple[pd.DataFrame, list[dict[str, str | int]]]:
    _validate_mail_credentials(config)

    mail = imaplib.IMAP4_SSL(config.mail.imap_server)
    mail.login(config.mail.email_address, config.mail.email_password)
    mail.select("inbox")

    _, data = mail.search(None, "ALL")
    mail_ids = data[0].split()
    latest_mail_ids = mail_ids[-count:]

    mail_rows: list[dict[str, str]] = []
    pdf_rows: list[dict[str, str | int]] = []

    for mail_index, mail_id in enumerate(reversed(latest_mail_ids)):
        _, data = mail.fetch(mail_id, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        sender = decode_text(msg["From"])
        subject = decode_text(msg["Subject"])
        body = get_body(msg)
        full_text = f"{subject} {body}"

        attachment_yn = has_attachment(msg)
        category = classify_mail(full_text)
        status = get_status(full_text, attachment_yn)
        priority, deadline = analyze_priority_deadline(full_text)

        mail_rows.append(
            MailRecord(
                sender=sender,
                subject=subject,
                body=body,
                category=category,
                priority=priority,
                status=status,
                deadline=deadline,
                has_attachment=attachment_yn,
            ).to_dict()
        )

        pdf_path = download_pdf_attachment(msg, config.paths.download_dir)
        if pdf_path:
            pdf_rows.append(
                PdfAttachment(
                    mail_index=mail_index,
                    pdf_path=str(pdf_path),
                    mail_subject=subject,
                    sender=sender,
                ).to_dict()
            )

    mail.logout()
    return pd.DataFrame(mail_rows), pdf_rows


def save_mail_csv(df: pd.DataFrame, filename: str = "mail_task_list.csv") -> None:
    if df.empty:
        raise ValueError("저장할 메일 데이터가 없습니다.")

    df.to_csv(filename, index=False, encoding="utf-8-sig")


def _validate_mail_credentials(config: AppConfig) -> None:
    if not config.mail.email_address or not config.mail.email_password:
        raise ValueError(
            "이메일 계정 정보가 없습니다. EMAIL_ADDRESS, EMAIL_PASSWORD 환경변수를 설정하세요."
        )

