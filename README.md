# emailprj

노트북 중심으로 작성된 메일 자동화 코드를 `app/` 패키지 구조로 정리했고, 같은 로직을 사용하는 `Streamlit` UI도 추가했습니다.

## 구조

- `app/config.py`: 환경변수, 서버, 경로 설정
- `app/constants.py`: 답장 템플릿, PDF 분석용 불용어
- `app/services/`: 메일 조회, 분류, 발송, PDF 추출, 요약
- `app/analysis/`: 대시보드, 필터, PDF 시각화
- `app/models/`: 데이터 구조
- `streamlit_app.py`: 브라우저 UI 엔트리포인트

## 준비

1. `.env.example` 내용을 참고해서 환경변수를 준비합니다.
2. 최소한 `EMAIL_ADDRESS`, `EMAIL_PASSWORD`는 메일 조회와 답장 전송에 필요합니다.
3. `GOOGLE_API_KEY`는 PDF 3줄 요약 기능에 필요합니다.

## CLI 확인 실행

```bash
python -m app.main
```

## Streamlit 실행

먼저 Streamlit이 설치되어 있지 않다면 설치합니다.

```bash
pip install streamlit
```

그다음 아래 명령으로 실행합니다.

```bash
streamlit run streamlit_app.py
```

또는 Python 모듈 방식으로 실행할 수도 있습니다.

```bash
python -m streamlit run streamlit_app.py
```

실행 후 브라우저에서 기본적으로 `http://localhost:8501`로 접속하면 됩니다.

## Streamlit 화면 기능

- 최신 메일 불러오기
- 메일 목록 조회
- 우선 처리 추천 표
- 메일 통계 대시보드
- 조건별 메일 필터
- 처리상태 변경
- 답장 템플릿 선택 후 전송
- 첨부 PDF 키워드 분석, 워드클라우드, 3줄 요약
