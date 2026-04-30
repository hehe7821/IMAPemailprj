from __future__ import annotations

import pandas as pd


def filter_mails(
    df: pd.DataFrame,
    *,
    sender_keyword: str | None = None,
    subject_keyword: str | None = None,
    category: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    only_with_attachment: bool = False,
    only_with_deadline: bool = False,
) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    result_df = df.copy()
    result_df["마감일"] = pd.to_datetime(result_df["마감일"], errors="coerce")

    if sender_keyword:
        result_df = result_df[
            result_df["보낸 사람"].str.contains(sender_keyword, case=False, na=False)
        ]
    if subject_keyword:
        result_df = result_df[result_df["제목"].str.contains(subject_keyword, case=False, na=False)]
    if category:
        result_df = result_df[result_df["분류"] == category]
    if priority:
        result_df = result_df[result_df["우선순위"] == priority]
    if status:
        result_df = result_df[result_df["처리상태"] == status]
    if only_with_attachment:
        result_df = result_df[result_df["첨부파일여부"] == "Y"]
    if only_with_deadline:
        result_df = result_df[result_df["마감일"].notna()]

    return result_df


def update_mail_status(df: pd.DataFrame, row_index: int, new_status: str) -> pd.DataFrame:
    if row_index < 0 or row_index >= len(df):
        raise IndexError("유효하지 않은 메일 index입니다.")

    result_df = df.copy()
    result_df.loc[result_df.index[row_index], "처리상태"] = new_status
    return result_df

