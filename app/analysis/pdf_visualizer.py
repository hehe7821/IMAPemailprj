from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from nltk import Text
from PIL import Image
from wordcloud import WordCloud


def build_top_nouns_chart(pdf_df: pd.DataFrame, stop_words: list[str], idx: int) -> plt.Figure:
    nouns = [word for word in pdf_df["nouns"][idx] if word not in stop_words]
    text = Text(nouns)
    top10_df = pd.DataFrame(text.vocab().most_common(10), columns=["noun", "count"])

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=top10_df, x="noun", y="count", hue="noun", legend=False, ax=ax)
    ax.set_title(f"{pdf_df['title'][idx]} 상위 10개 명사")
    ax.set_xlabel("명사")
    ax.set_ylabel("빈도")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig


def build_wordcloud_figure(
    pdf_df: pd.DataFrame,
    stop_words: list[str],
    idx: int,
    cloud_image_path: str | Path,
) -> plt.Figure:
    mask_image = Image.open(cloud_image_path).convert("RGBA")
    mask_array = np.array(mask_image)

    wordcloud = WordCloud(
        background_color="white",
        relative_scaling=0.2,
        font_path=r"C:\Windows\Fonts\malgun.ttf",
        stopwords=stop_words,
        max_words=50,
        mask=mask_array,
    )
    wordcloud.generate(pdf_df["document"][idx])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.imshow(wordcloud)
    ax.set_title(pdf_df["title"][idx])
    ax.axis("off")
    fig.tight_layout()
    return fig

