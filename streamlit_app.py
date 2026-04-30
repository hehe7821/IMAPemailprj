from __future__ import annotations

from email.utils import parseaddr
from pathlib import Path

import pandas as pd
import streamlit as st

from app.analysis.dashboard import build_mail_dashboard_figure, recommend_priority_mails
from app.analysis.filters import filter_mails, update_mail_status
from app.analysis.pdf_visualizer import build_top_nouns_chart, build_wordcloud_figure
from app.config import load_config
from app.constants import REPLY_TEMPLATES, STOP_WORDS
from app.services.mail_reader import load_recent_emails, save_mail_csv
from app.services.mail_sender import build_reply_candidates, send_reply
from app.services.pdf_service import add_document_column, add_nouns_column, pdfs_to_df
from app.services.summary_service import summarize_pdf_text_3lines


BASE_DIR = Path(__file__).resolve().parent
CONFIG = load_config(BASE_DIR)
STATUS_OPTIONS = ["미처리", "처리 필요", "답장 필요", "첨부 확인 필요", "처리 완료"]


def init_session_state() -> None:
    if "mail_df" not in st.session_state:
        st.session_state.mail_df = pd.DataFrame()
    if "pdf_df" not in st.session_state:
        st.session_state.pdf_df = pd.DataFrame()
    if "pdf_meta" not in st.session_state:
        st.session_state.pdf_meta = []


def refresh_mail_data(count: int) -> None:
    mail_df, pdf_meta = load_recent_emails(CONFIG, count)
    st.session_state.mail_df = mail_df
    st.session_state.pdf_meta = pdf_meta

    if pdf_meta:
        pdf_paths = [item["pdf_path"] for item in pdf_meta]
        pdf_df = pdfs_to_df(pdf_paths)
        if not pdf_df.empty:
            pdf_df = add_nouns_column(pdf_df)
            pdf_df = add_document_column(pdf_df)
            meta_df = pd.DataFrame(pdf_meta)
            pdf_df["메일index"] = meta_df["메일index"]
            pdf_df["메일제목"] = meta_df["메일제목"]
            pdf_df["보낸사람"] = meta_df["보낸사람"]
        st.session_state.pdf_df = pdf_df
    else:
        st.session_state.pdf_df = pd.DataFrame()


def render_sidebar() -> None:
    st.sidebar.header("데이터 불러오기")
    count = st.sidebar.number_input("최신 메일 개수", min_value=1, value=10, step=1)

    if st.sidebar.button("메일 불러오기", use_container_width=True):
        try:
            refresh_mail_data(int(count))
            st.sidebar.success(f"메일 {len(st.session_state.mail_df)}건을 불러왔습니다.")
        except Exception as exc:
            st.sidebar.error(str(exc))

    if st.sidebar.button("CSV 저장", use_container_width=True):
        try:
            save_mail_csv(st.session_state.mail_df)
            st.sidebar.success("mail_task_list.csv 저장 완료")
        except Exception as exc:
            st.sidebar.error(str(exc))

    st.sidebar.divider()
    st.sidebar.caption("필수 환경변수")
    st.sidebar.code("EMAIL_ADDRESS\nEMAIL_PASSWORD\nGOOGLE_API_KEY", language="text")


def render_mail_overview() -> None:
    st.subheader("메일 목록")
    if st.session_state.mail_df.empty:
        st.info("사이드바에서 메일을 먼저 불러오세요.")
        return

    st.dataframe(st.session_state.mail_df, use_container_width=True)


def render_priority_section() -> None:
    st.subheader("우선 처리 추천")
    if st.session_state.mail_df.empty:
        return

    recommended_df = recommend_priority_mails(st.session_state.mail_df)
    if recommended_df.empty:
        st.success("현재 우선 처리할 메일이 없습니다.")
        return

    st.dataframe(recommended_df, use_container_width=True)


def render_dashboard_section() -> None:
    st.subheader("메일 대시보드")
    if st.session_state.mail_df.empty:
        return

    figure = build_mail_dashboard_figure(st.session_state.mail_df)
    st.pyplot(figure, clear_figure=True, use_container_width=True)


def render_filter_section() -> None:
    st.subheader("메일 필터")
    if st.session_state.mail_df.empty:
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        sender_keyword = st.text_input("보낸 사람")
        category = st.selectbox(
            "분류",
            ["전체"] + sorted(st.session_state.mail_df["분류"].dropna().unique().tolist()),
        )
    with col2:
        subject_keyword = st.text_input("제목 키워드")
        priority = st.selectbox("우선순위", ["전체", "높음", "중간", "낮음"])
    with col3:
        status = st.selectbox("처리상태", ["전체"] + STATUS_OPTIONS)
        only_with_attachment = st.checkbox("첨부파일만")
        only_with_deadline = st.checkbox("마감일 있는 메일만")

    filtered_df = filter_mails(
        st.session_state.mail_df,
        sender_keyword=sender_keyword or None,
        subject_keyword=subject_keyword or None,
        category=None if category == "전체" else category,
        priority=None if priority == "전체" else priority,
        status=None if status == "전체" else status,
        only_with_attachment=only_with_attachment,
        only_with_deadline=only_with_deadline,
    )
    st.caption(f"검색 결과: {len(filtered_df)}건")
    st.dataframe(filtered_df, use_container_width=True)


def render_status_section() -> None:
    st.subheader("처리상태 변경")
    if st.session_state.mail_df.empty:
        return

    row_index = st.number_input(
        "변경할 메일 index",
        min_value=0,
        max_value=max(len(st.session_state.mail_df) - 1, 0),
        value=0,
        step=1,
    )
    new_status = st.selectbox("새 처리상태", STATUS_OPTIONS)

    if st.button("처리상태 반영"):
        try:
            st.session_state.mail_df = update_mail_status(
                st.session_state.mail_df,
                int(row_index),
                new_status,
            )
            st.success("처리상태를 변경했습니다.")
        except Exception as exc:
            st.error(str(exc))


def render_reply_section() -> None:
    st.subheader("자동 답장")
    if st.session_state.mail_df.empty:
        return

    candidates = build_reply_candidates(st.session_state.mail_df)
    if candidates.empty:
        st.info("답장 후보 메일이 없습니다.")
        return

    st.dataframe(candidates, use_container_width=True)
    row_index = st.number_input(
        "답장할 메일 index",
        min_value=0,
        max_value=max(len(st.session_state.mail_df) - 1, 0),
        value=0,
        step=1,
        key="reply_row_index",
    )

    template_label_map = {
        f"{key}. {value['title']}": key for key, value in REPLY_TEMPLATES.items()
    }
    selected_label = st.selectbox("답장 템플릿", list(template_label_map.keys()))
    selected_template = REPLY_TEMPLATES[template_label_map[selected_label]]

    selected_mail = st.session_state.mail_df.iloc[int(row_index)]
    sender_email = parseaddr(selected_mail["보낸 사람"])[1]
    st.text_input("받는 사람", value=sender_email, disabled=True)
    st.text_input("제목", value=f"Re: {selected_mail['제목']}", disabled=True)
    st.text_area("본문", value=selected_template["body"], height=180, disabled=True)

    if st.button("답장 전송"):
        try:
            send_reply(CONFIG, sender_email, selected_mail["제목"], selected_template)
            st.success("답장을 전송했습니다.")
        except Exception as exc:
            st.error(str(exc))


def render_pdf_section() -> None:
    st.subheader("첨부 PDF 분석")
    if st.session_state.pdf_df.empty:
        st.info("PDF 첨부파일이 있는 메일을 불러오면 이 영역이 활성화됩니다.")
        return

    pdf_df = st.session_state.pdf_df
    selected_idx = st.selectbox(
        "문서 선택",
        options=list(range(len(pdf_df))),
        format_func=lambda idx: f"{idx}. {pdf_df.iloc[idx]['title']}",
    )

    selected_row = pdf_df.iloc[selected_idx]
    st.write(f"메일 제목: {selected_row['메일제목']}")
    st.write(f"보낸 사람: {selected_row['보낸사람']}")

    with st.expander("문서 원문 보기"):
        st.text(selected_row["content"][:5000])

    col1, col2 = st.columns(2)
    with col1:
        noun_figure = build_top_nouns_chart(pdf_df, STOP_WORDS, selected_idx)
        st.pyplot(noun_figure, clear_figure=True, use_container_width=True)
    with col2:
        cloud_figure = build_wordcloud_figure(
            pdf_df,
            STOP_WORDS,
            selected_idx,
            CONFIG.paths.cloud_image_path,
        )
        st.pyplot(cloud_figure, clear_figure=True, use_container_width=True)

    if st.button("3줄 요약 생성"):
        try:
            summary = summarize_pdf_text_3lines(
                CONFIG,
                selected_row["title"],
                selected_row["content"],
            )
            st.text(summary)
        except Exception as exc:
            st.error(str(exc))


def main() -> None:
    st.set_page_config(page_title="메일 자동화 대시보드", layout="wide")
    init_session_state()

    st.title("메일 자동화 대시보드")
    st.caption("메일 업무 자동화를 위해 디자인 되었습니다.")

    render_sidebar()
    render_mail_overview()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["우선순위", "대시보드", "필터", "답장/상태", "PDF 분석"]
    )

    with tab1:
        render_priority_section()
    with tab2:
        render_dashboard_section()
    with tab3:
        render_filter_section()
    with tab4:
        render_status_section()
        st.divider()
        render_reply_section()
    with tab5:
        render_pdf_section()


if __name__ == "__main__":
    main()
