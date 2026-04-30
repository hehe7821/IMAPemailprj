from __future__ import annotations

import re
from datetime import datetime, timedelta


CATEGORY_KEYWORDS = {
    "회의/일정": ["회의", "미팅", "일정", "참석", "zoom", "meet"],
    "마감/제출": ["마감", "제출", "기한", "오늘까지", "내일까지", "보고서"],
    "결제/영수증": ["결제", "영수증", "청구서", "입금", "세금계산서"],
    "문의/요청": ["문의", "요청", "확인 부탁", "검토", "회신", "답변"],
    "광고/홍보": ["이벤트", "할인", "프로모션", "뉴스레터", "쿠폰"],
}

HIGH_PRIORITY_KEYWORDS = [
    "긴급",
    "asap",
    "오늘까지",
    "내일까지",
    "익일까지",
    "금일까지",
    "마감",
    "중요",
]
MIDDLE_PRIORITY_KEYWORDS = ["확인 부탁", "검토", "회신", "요청", "문의"]
DEADLINE_KEYWORDS = ["마감", "제출", "기한", "까지", "due"]


def classify_mail(text: str) -> str:
    lowered = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            return category
    return "기타"


def get_status(text: str, attachment_yn: str) -> str:
    if any(keyword in text for keyword in ["회신", "답변", "확인 부탁", "검토 요청"]):
        return "답장 필요"
    if any(keyword in text for keyword in ["마감", "제출", "기한", "오늘까지", "내일까지"]):
        return "처리 필요"
    if attachment_yn == "Y":
        return "첨부 확인 필요"
    return "미처리"


def analyze_priority_deadline(text: str, today: datetime | None = None) -> tuple[str, str]:
    today = today or datetime.today()
    text_lower = text.lower()
    deadline = ""

    if any(keyword in text_lower for keyword in DEADLINE_KEYWORDS):
        if any(keyword in text for keyword in ["오늘까지", "금일까지", "당일까지"]):
            deadline = today.strftime("%Y-%m-%d")
        elif any(keyword in text for keyword in ["내일까지", "익일까지"]) or (
            "익일" in text and "까지" in text
        ):
            deadline = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            deadline = _extract_explicit_deadline(text, today)

    priority = "낮음"

    if deadline:
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
        remain_days = (deadline_date.date() - today.date()).days
        if remain_days <= 3:
            priority = "높음"
        elif remain_days <= 5:
            priority = "중간"

    if any(keyword in text_lower for keyword in HIGH_PRIORITY_KEYWORDS):
        priority = "높음"
    elif any(keyword in text_lower for keyword in MIDDLE_PRIORITY_KEYWORDS):
        priority = "중간"

    return priority, deadline


def _extract_explicit_deadline(text: str, today: datetime) -> str:
    full_date_match = re.search(r"(\d{4})[.-](\d{1,2})[.-](\d{1,2})", text)
    if full_date_match:
        year, month, day = full_date_match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"

    month_day_match = re.search(r"(\d{1,2})월\s*(\d{1,2})일", text)
    if month_day_match:
        month, day = month_day_match.groups()
        return f"{today.year}-{int(month):02d}-{int(day):02d}"

    return ""

