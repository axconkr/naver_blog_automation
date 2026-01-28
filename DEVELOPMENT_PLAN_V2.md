# 2차 개발 계획서

## 개요
엑셀 원고 기반 워드 문서 생성 + AI 이미지 생성 + 네이버 블로그 발행

## 워크플로우
1. 엑셀 읽기 (주제, 원고)
2. Gemini로 본문 생성 및 섹션 구분
3. 워드 문서 생성 (섹션별 정리)
4. 나노바나나로 섹션별 이미지 생성
5. 워드에 이미지 삽입
6. 사용자 검토/수정
7. 네이버 블로그에 글+이미지 발행

## 파일 구조
```
naver_blog_V1/
├── nanobanana.py      # 나노바나나 이미지 생성 API
├── create_word.py     # 워드 문서 생성
├── image_prompt.py    # 이미지 프롬프트 생성
├── upload_bot.py      # 블로그 업로드 (이미지 포함)
├── app.py             # GUI
└── images/            # 생성된 이미지 저장
```

## API 정보
- 나노바나나: Gemini API 기반 (imagen-3.0-generate-002)
- 기존 GEMINI_API_KEY 사용
