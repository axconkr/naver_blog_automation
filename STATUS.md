# 네이버 블로그 자동화 프로젝트 - 상태 모니터링

**마지막 업데이트**: 2026-01-24 22:52

---

## 프로젝트 개요

Selenium + Gemini API 기반 네이버 블로그 자동 포스팅 시스템

### 워크플로우
```
1. excel_create.py  → blog{날짜}.xlsx 생성 (제목 5개)
2. create.py        → Gemini API로 본문 생성 → 원본 blog*.xlsx에 저장
3. upload_bot.py    → blog*.xlsx 읽어서 네이버 블로그에 업로드
```

---

## 현재 파일 구조

```
naver_blog_V1/
├── app.py              # GUI 앱 (tkinter)
├── excel_create.py     # 엑셀 파일 생성
├── create.py           # Gemini API로 블로그 본문 생성
├── gemini.py           # Gemini API 유틸리티
├── upload_bot.py       # 네이버 블로그 업로드
├── login.py            # 로그인 테스트
├── requirements.txt    # 의존성 목록
├── .env                # 환경 변수
├── .gitignore          # Git 제외 파일
├── README.md           # 프로젝트 문서
├── STATUS.md           # 이 파일
└── venv/               # 가상환경
```

---

## 환경 분석

| 항목 | 현재 상태 | 비고 |
|------|----------|------|
| OS | macOS (Darwin) | |
| Python (venv) | 3.9 | |
| Chrome | 144.0.7559.97 | ✅ 설치됨 |
| selenium | ✅ 설치됨 | venv |
| pyperclip | ✅ 설치됨 | venv |
| python-dotenv | ✅ 설치됨 | venv |
| google-generativeai | ✅ 설치됨 | venv |
| Git | ✅ 초기화됨 | |

---

## 구현 현황

| 기능 | 상태 | 파일 | 비고 |
|------|------|------|------|
| GUI 앱 | ✅ 완료 | app.py | tkinter 기반 |
| 엑셀 생성 | ✅ 완료 | excel_create.py | 샘플 제목 5개 |
| 본문 생성 | ✅ 완료 | create.py | Gemini API |
| 네이버 로그인 | ✅ 완료 | upload_bot.py | Mac/Windows 호환 |
| 블로그 업로드 | ✅ 완료 | upload_bot.py | |
| 로그인 테스트 | ✅ 완료 | login.py | .env 연동 + Mac 호환 |

---

## 수정 완료된 항목 (2026-01-24)

### ✅ Critical 문제 해결

1. **`.env` 파일 형식** - 등호 사용, 공백 제거, GEMINI_API_KEY 추가됨
2. **Mac 호환성** - `Keys.COMMAND` / `Keys.CONTROL` 자동 선택 (platform 모듈 사용)
3. **login.py .env 연동** - python-dotenv 적용
4. **파일명 불일치 해결** - create.py가 원본 blog*.xlsx에 저장
5. **파일명 오타 수정** - exel_crete.py → excel_create.py

### ✅ Warning 문제 해결

6. **의존성 설치** - venv에 모든 패키지 설치 완료
7. **Git 초기화** - .gitignore 포함 설정 완료

---

## 실행 방법

```bash
# 1. 가상환경 활성화
source venv/bin/activate

# 2. GUI 실행
python app.py

# 또는 개별 스크립트 실행
python excel_create.py  # 엑셀 생성
python create.py        # 본문 생성
python upload_bot.py    # 업로드
```

---

## 남은 개선 사항 (선택)

- [ ] 에러 핸들링 강화 (로그인 실패 시 재시도)
- [ ] 캡차/2단계 인증 대응
- [ ] logging 모듈 도입
- [ ] 브라우저 자동 종료 옵션

---

## 참고사항

- 네이버는 봇 탐지가 있어 직접 `send_keys` 대신 클립보드 붙여넣기 방식 사용
- headless 모드는 현재 비활성화 상태 (디버깅용)
- Gemini API 사용 시 비용 발생 가능
- 네이버 정책에 따라 자동 로그인이 차단될 수 있음 (캡차, 2단계 인증)
