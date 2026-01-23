# 개발 현황 (Changelog)

## v1.1.0 - 2026-01-24

### 새로운 기능

#### 1. 발행 기능 완성
- 네이버 블로그 에디터에서 실제 글 발행 성공
- iframe 내부 발행 버튼 클릭 로직 구현
- 도움말 패널 자동 닫기 처리
- 발행 확인 모달 처리

#### 2. 카테고리 선택 기능
- 발행 시 카테고리 자동 선택
- 엑셀 C열에서 카테고리명 읽기
- 드롭다운에서 카테고리명으로 검색하여 선택

#### 3. 예약 발행 기능
- 발행 시간 예약 설정
- 엑셀 D열에서 예약 시간 읽기 (형식: YYYY-MM-DD HH:MM)
- 시간/분 자동 선택 (분은 10분 단위)

#### 4. GUI 예약 발행 설정
- "예약 발행 사용" 체크박스
- 시작 날짜 입력 (YYYY-MM-DD)
- 시작 시간 선택 (시/분)
- 글 간격 설정 (분 단위)
- 업로드 시 자동으로 엑셀 D열에 예약 시간 계산하여 입력

### 버그 수정
- Gemini 모델명 변경: `gemini-1.5-pro` → `gemini-2.5-flash`
- create.py f-string 문법 오류 수정
- venv Python 강제 사용 (`get_python_executable()`)

### 파일 변경 내역

| 파일 | 변경 내용 |
|------|----------|
| `app.py` | GUI에 예약 발행 설정 섹션 추가, 엑셀 D열 자동 업데이트 로직 |
| `upload_bot.py` | 카테고리 선택, 예약 발행, iframe 내부 발행 로직 |
| `excel_create.py` | C열(카테고리), D열(발행시간) 컬럼 추가 |
| `create.py` | Gemini 모델명 수정, 문법 오류 수정 |

### 엑셀 파일 구조

| 열 | 헤더 | 설명 |
|----|------|------|
| A | 제목 | 블로그 글 제목 |
| B | 본문 | 블로그 본문 (Gemini로 생성) |
| C | 카테고리 | 블로그 카테고리명 |
| D | 발행시간 | 예약 발행 시간 (YYYY-MM-DD HH:MM) |

### 셀렉터 정보 (네이버 블로그 에디터)

```
제목 입력: .se-section-documentTitle .se-text-paragraph
본문 입력: .se-section-text .se-text-paragraph
발행 버튼: .publish_btn__m9KHH
발행 확인: button.confirm_btn__WEaBq
카테고리 드롭다운: .selectbox_button__jb1Dt
카테고리 목록: .option_list_layer__YX1Tq label.radio_label__mB6ia
예약 라디오: input#radio_time2[value='pre']
시간 선택: select.hour_option__J_heO
분 선택: select.minute_option__Vb3xB
```

---

## v1.0.0 - 2026-01-24 (Initial)

### 기본 기능
- 엑셀 파일 생성 (excel_create.py)
- Gemini API로 블로그 본문 생성 (create.py)
- 네이버 로그인 (upload_bot.py)
- 블로그 글쓰기 페이지 제목/본문 입력
- GUI 앱 (app.py)
