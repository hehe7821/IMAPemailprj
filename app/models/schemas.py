from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class MailRecord:
    sender: str
    subject: str
    body: str
    category: str
    priority: str
    status: str
    deadline: str
    has_attachment: str

    def to_dict(self) -> dict[str, str]:
        return {
            "보낸 사람": self.sender,
            "제목": self.subject,
            "본문": self.body,
            "분류": self.category,
            "우선순위": self.priority,
            "처리상태": self.status,
            "마감일": self.deadline,
            "첨부파일여부": self.has_attachment,
        }


@dataclass(slots=True)
class PdfAttachment:
    mail_index: int
    pdf_path: str
    mail_subject: str
    sender: str

    def to_dict(self) -> dict[str, str | int]:
        return {
            "메일index": self.mail_index,
            "pdf_path": self.pdf_path,
            "메일제목": self.mail_subject,
            "보낸사람": self.sender,
        }


@dataclass(slots=True)
class ReplyTemplate:
    title: str
    body: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

