from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def recommend_priority_mails(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    result_df = df.copy()
    result_df["마감일"] = pd.to_datetime(result_df["마감일"], errors="coerce")
    filtered_df = result_df[
        (result_df["우선순위"].isin(["높음", "중간"])) & (result_df["처리상태"] != "처리 완료")
    ].copy()

    if filtered_df.empty:
        return filtered_df

    priority_order = {"높음": 0, "중간": 1}
    filtered_df["우선순위정렬"] = filtered_df["우선순위"].map(priority_order)
    return filtered_df.sort_values(by=["우선순위정렬", "마감일"], ascending=[True, True])


def build_mail_dashboard_figure(df: pd.DataFrame) -> plt.Figure:
    result_df = df.copy()
    result_df["마감일"] = pd.to_datetime(result_df["마감일"], errors="coerce")
    today = pd.Timestamp.today().normalize()
    result_df["남은일수"] = (result_df["마감일"] - today).dt.days

    sns.set(style="whitegrid")
    plt.rcParams["font.family"] = "Malgun Gothic"

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("메일 업무 종합 분석 대시보드", fontsize=18)

    sns.countplot(
        data=result_df,
        x="처리상태",
        order=result_df["처리상태"].value_counts().index,
        ax=axes[0, 0],
    )
    axes[0, 0].set_title("처리상태별 메일 수")
    axes[0, 0].set_xlabel("")
    axes[0, 0].set_ylabel("메일 수")
    axes[0, 0].tick_params(axis="x", rotation=30)

    sns.countplot(
        data=result_df,
        x="분류",
        order=result_df["분류"].value_counts().index,
        ax=axes[0, 1],
    )
    axes[0, 1].set_title("분류별 메일 수")
    axes[0, 1].set_xlabel("")
    axes[0, 1].set_ylabel("메일 수")
    axes[0, 1].tick_params(axis="x", rotation=30)

    sns.countplot(
        data=result_df,
        x="우선순위",
        order=["높음", "중간", "낮음"],
        ax=axes[1, 0],
    )
    axes[1, 0].set_title("우선순위별 메일 수")
    axes[1, 0].set_xlabel("")
    axes[1, 0].set_ylabel("메일 수")

    deadline_df = result_df[result_df["남은일수"].notna()]
    sns.stripplot(
        data=deadline_df,
        x="남은일수",
        hue="우선순위",
        palette={"높음": "red", "중간": "orange", "낮음": "green"},
        ax=axes[1, 1],
        jitter=True,
    )
    axes[1, 1].set_title("마감일까지 남은 일수")
    axes[1, 1].set_xlabel("남은 일수")
    axes[1, 1].set_ylabel("")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return fig

