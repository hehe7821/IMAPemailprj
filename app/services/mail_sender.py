from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd

from app.config import AppConfig


def build_reply_candidates(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    result_df = df.copy()
    result_df["마감일"] = pd.to_datetime(result_df["마감일"], errors="coerce")
    filtered_df = result_df[result_df["우선순위"].isin(["높음", "중간"])].copy()

    if filtered_df.empty:
        return filtered_df

    priority_order = {"높음": 0, "중간": 1}
    filtered_df["우선순위정렬"] = filtered_df["우선순위"].map(priority_order)
    return filtered_df.sort_values(by=["우선순위정렬", "마감일"], ascending=[True, True])


def send_reply(
    config: AppConfig,
    to_email: str,
    original_subject: str,
    template: dict[str, str],
) -> None:
    if not config.mail.email_address or not config.mail.email_password:
        raise ValueError(
            "이메일 계정 정보가 없습니다. EMAIL_ADDRESS, EMAIL_PASSWORD 환경변수를 설정하세요."
        )

    reply_subject = f"Re: {original_subject}"
    msg = MIMEMultipart()
    msg["From"] = config.mail.email_address
    msg["To"] = to_email
    msg["Subject"] = reply_subject
    msg.attach(MIMEText(template["body"], "plain", "utf-8"))

    with smtplib.SMTP(config.mail.smtp_server, config.mail.smtp_port) as server:
        server.starttls()
        server.login(config.mail.email_address, config.mail.email_password)
        server.send_message(msg)

