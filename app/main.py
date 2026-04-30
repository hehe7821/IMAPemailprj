from __future__ import annotations

from pathlib import Path

from app.config import load_config


def bootstrap() -> None:
    config = load_config(Path(__file__).resolve().parents[1])
    print("구조화된 이메일 자동화 패키지가 준비되었습니다.")
    print(f"- 다운로드 폴더: {config.paths.download_dir}")
    print("- 다음 단계에서 Streamlit 엔트리포인트를 추가하면 됩니다.")


if __name__ == "__main__":
    bootstrap()

