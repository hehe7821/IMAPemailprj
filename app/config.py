from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class MailConfig:
    imap_server: str = "imap.gmail.com"
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_address: str = ""
    email_password: str = ""


@dataclass(slots=True)
class AIConfig:
    google_api_key: str = ""
    summary_model: str = "gemma-4-26b-a4b-it"


@dataclass(slots=True)
class PathConfig:
    base_dir: Path
    download_dir: Path
    cloud_image_path: Path


@dataclass(slots=True)
class AppConfig:
    mail: MailConfig
    ai: AIConfig
    paths: PathConfig


def load_config(base_dir: Path | None = None) -> AppConfig:
    base_dir = base_dir or Path(__file__).resolve().parents[1]
    _load_dotenv(base_dir / ".env")

    download_dir = Path(os.getenv("DOWNLOAD_DIR", base_dir / "downloads"))
    cloud_image_path = Path(os.getenv("CLOUD_IMAGE_PATH", base_dir / "cloud.png"))

    download_dir.mkdir(parents=True, exist_ok=True)

    return AppConfig(
        mail=MailConfig(
            imap_server=os.getenv("IMAP_SERVER", "imap.gmail.com"),
            smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            email_address=os.getenv("EMAIL_ADDRESS", ""),
            email_password=os.getenv("EMAIL_PASSWORD", ""),
        ),
        ai=AIConfig(
            google_api_key=os.getenv("GOOGLE_API_KEY", ""),
            summary_model=os.getenv("SUMMARY_MODEL", "gemma-4-26b-a4b-it"),
        ),
        paths=PathConfig(
            base_dir=base_dir,
            download_dir=download_dir,
            cloud_image_path=cloud_image_path,
        ),
    )


def _load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            continue

        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]

        os.environ.setdefault(key, value)
