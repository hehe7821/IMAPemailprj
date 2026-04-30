from __future__ import annotations

from app.config import AppConfig


def summarize_pdf_text_3lines(config: AppConfig, pdf_title: str, pdf_text: str) -> str:
    if not config.ai.google_api_key:
        raise ValueError("GOOGLE_API_KEY 환경변수가 설정되어 있지 않습니다.")

    from google import genai

    client = genai.Client(api_key=config.ai.google_api_key)
    prompt = f"""
당신은 문서 요약 전문가입니다.
주어진 문서를 아래 형식으로 정확히 3줄 요약하세요.

출력 형식:
1. 문서주제: 문서가 무엇에 관한 문서인지
2. 핵심내용: 가장 중요한 정보 2~3개를 압축한 내용
3. 해야할 일/주의사항: 독자가 실제로 유의하거나 수행해야 할 사항

규칙:
- 반드시 위 3줄만 출력, 그 외 어떤 말도 추가하지 말 것
- 각 줄은 한 문장
- 세 줄의 내용이 서로 중복되지 않아야 함
- 문서에 없는 내용은 추측하지 말 것
- 일정, 조건, 제한, 예외가 있으면 3번에 우선 반영할 것
- 3번에 해당 사항이 없으면 "해야할 일/주의사항: 해당 없음"으로 출력

문서 제목:
{pdf_title}

문서 내용:
{pdf_text}
""".strip()

    response = client.models.generate_content(
        model=config.ai.summary_model,
        contents=prompt,
    )
    return response.text.strip()

