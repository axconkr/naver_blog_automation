# 구글 드라이브 이미지 인덱서 및 블로그 통합 가이드

네이버 블로그 작성 시 구글 드라이브의 이미지를 자동으로 분석하고 문맥에 맞는 이미지를 추천하는 시스템입니다.

## 주요 기능

### 1. 이미지 인덱싱 (`gdrive_image_indexer.py`)
- **구글 드라이브 폴더 접근**: OAuth 2.0 인증으로 안전하게 접근
- **이미지 메타데이터 추출**: 파일명, 크기, 생성/수정 날짜, 링크 등
- **AI 비전 분석**: Gemini를 사용해 이미지 내용 자동 분석
  - 상세 설명 (한국어)
  - 관련 태그/키워드
  - 카테고리 분류
  - 주요 색상
  - 분위기/느낌
  - 피사체 목록
  - 적합한 블로그 문맥
- **JSON 인덱스 생성**: 분석 결과를 `image_index.json`으로 저장

### 2. 블로그 이미지 통합 (`blog_image_integrator.py`)
- **문맥 기반 이미지 추천**: 블로그 텍스트 분석 후 적합한 이미지 자동 추천
- **섹션별 이미지 매칭**: 문단별로 관련 이미지 제안
- **네이버 블로그 자동 삽입**: Selenium을 통한 이미지 자동 업로드

## 설치

```bash
pip install -r requirements.txt
```

필요한 패키지:
- `google-auth>=2.25.0`
- `google-auth-oauthlib>=1.2.0`
- `google-auth-httplib2>=0.2.0`
- `google-api-python-client>=2.110.0`
- `google-generativeai>=0.3.0`

## 구글 API 설정

### 1. Google Cloud Console 설정
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성 (또는 기존 프로젝트 선택)
3. **API 및 서비스** → **라이브러리** 에서 다음 API 활성화:
   - Google Drive API
   - Google Gemini API (이미 활성화되어 있을 수 있음)

### 2. OAuth 2.0 인증 정보 생성
1. **API 및 서비스** → **사용자 인증 정보**
2. **사용자 인증 정보 만들기** → **OAuth 클라이언트 ID**
3. 애플리케이션 유형: **데스크톱 앱**
4. 이름 입력 후 생성
5. JSON 다운로드 → 프로젝트 폴더에 `credentials.json`으로 저장

### 3. .env 파일 설정
```env
GEMINI_API_KEY=your_gemini_api_key
```

## 사용 방법

### 1단계: 이미지 인덱스 생성

```python
from gdrive_image_indexer import GDriveImageIndexer
from dotenv import load_dotenv
import os

load_dotenv()

# 초기화
gemini_api_key = os.getenv('GEMINI_API_KEY')
folder_url = "https://drive.google.com/drive/u/0/folders/1-5Ra55iS8j1HEj0AZxrSE0xpvAhya6pZ"

indexer = GDriveImageIndexer(gemini_api_key)

# 인증 (최초 1회만 필요, 이후 token.pickle 사용)
indexer.authenticate()

# 인덱스 생성
# sample_size=None이면 전체 이미지 분석 (시간 소요)
# sample_size=5 등으로 테스트 가능
index = indexer.build_index(folder_url, sample_size=10)

# 결과: image_index.json 파일 생성
```

**최초 실행 시:**
- 브라우저가 열리고 구글 계정 로그인 요청
- 권한 승인 후 `token.pickle` 파일 생성
- 이후에는 자동으로 인증됨

### 2단계: 블로그 작성 시 이미지 추천

```python
from blog_image_integrator import BlogImageIntegrator
from dotenv import load_dotenv
import os

load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')

# 초기화 (인덱스 파일 로드)
integrator = BlogImageIntegrator(gemini_api_key)
integrator.load_index()

# 블로그 텍스트 분석
blog_text = """
오늘은 맛있는 음식을 먹으러 갔습니다.
특히 파스타가 정말 맛있었어요.
"""

# 섹션별 이미지 추천
suggestions = integrator.analyze_blog_content_and_suggest(blog_text)

for suggestion in suggestions['suggestions']:
    print(f"섹션: {suggestion['section_text']}")
    for img in suggestion['recommended_images']:
        print(f"  - {img['filename']}: {img['description']}")
```

### 3단계: 특정 키워드로 이미지 검색

```python
# 키워드 기반 검색
results = indexer.search_images_by_context("음식", top_k=5)

for img in results:
    print(f"{img['filename']}")
    print(f"  설명: {img['description']}")
    print(f"  관련도: {img['relevance_score']}")
    print(f"  링크: {img['web_view_link']}")
```

## 생성되는 인덱스 구조 (`image_index.json`)

```json
{
  "folder_id": "1-5Ra55iS8j1HEj0AZxrSE0xpvAhya6pZ",
  "created_at": "2026-01-28T23:30:00",
  "total_images": 50,
  "images": [
    {
      "id": "1ABc...",
      "filename": "pasta_dish.jpg",
      "mime_type": "image/jpeg",
      "size": 2048576,
      "created_time": "2026-01-20T10:30:00Z",
      "modified_time": "2026-01-21T14:20:00Z",
      "web_view_link": "https://drive.google.com/file/d/...",
      "thumbnail_link": "https://...",
      "description": "크림 파스타가 담긴 흰색 접시, 포크와 함께 테이블 위에 놓여있음",
      "tags": ["파스타", "음식", "이탈리안", "크림소스", "레스토랑"],
      "category": "음식",
      "colors": ["화이트", "베이지", "옐로우"],
      "mood": "따뜻하고 맛있어 보이는",
      "subjects": ["파스타", "접시", "포크"],
      "context": "음식 리뷰, 레스토랑 방문기, 요리 레시피 블로그에 적합"
    }
  ]
}
```

## 네이버 블로그 통합 예시

```python
from selenium import webdriver
from blog_image_integrator import BlogImageIntegrator
import os
from dotenv import load_dotenv

load_dotenv()

# WebDriver 초기화
driver = webdriver.Chrome()

# 블로그 에디터로 이동 (네이버 로그인 필요)
driver.get("https://blog.naver.com/...")

# 이미지 추천
integrator = BlogImageIntegrator(os.getenv('GEMINI_API_KEY'))
integrator.load_index()

blog_text = "오늘의 맛집 방문기..."
suggestions = integrator.analyze_blog_content_and_suggest(blog_text)

# 추천된 이미지 자동 삽입
for suggestion in suggestions['suggestions']:
    for img in suggestion['recommended_images'][:1]:  # 섹션당 1개만
        image_url = img['web_view_link']
        integrator.insert_image_to_naver_blog(driver, image_url)
```

## 명령행 실행

```bash
# 인덱스 생성
python gdrive_image_indexer.py

# 이미지 추천 테스트
python blog_image_integrator.py
```

## 주의사항

### 1. API 할당량
- **Google Drive API**: 하루 10,000,000 요청
- **Gemini API**:
  - 무료 티어: 분당 60회 요청
  - 유료 티어: 더 높은 할당량

대량 이미지 분석 시 시간이 걸릴 수 있습니다.

### 2. 인증 파일 보안
- `credentials.json`: Git에 커밋하지 말 것 (`.gitignore` 추가 필요)
- `token.pickle`: 개인 액세스 토큰, 보안 유지 필요

### 3. 이미지 다운로드
- 이미지는 메모리에만 임시 저장
- `/tmp/` 폴더에 임시 파일 생성 후 자동 삭제

## 향후 개선 사항

1. **임베딩 기반 검색**: 현재는 키워드 매칭, 향후 벡터 임베딩으로 의미론적 검색 개선
2. **이미지 캐싱**: 자주 사용하는 이미지는 로컬 캐싱
3. **배치 분석**: 대량 이미지를 효율적으로 처리
4. **다국어 지원**: 현재는 한국어, 영어 등 다국어 태그 생성
5. **웹 UI**: GUI 기반 이미지 관리 인터페이스

## 트러블슈팅

### "credentials.json not found"
→ Google Cloud Console에서 OAuth 클라이언트 ID JSON 다운로드

### "API not enabled"
→ Google Cloud Console에서 Drive API 활성화

### Gemini API 할당량 초과
→ API 키 확인 또는 유료 플랜으로 업그레이드

### 이미지 분석 실패
→ 파일 형식 확인 (JPEG, PNG 등), 파일 크기 확인 (Gemini 제한: 20MB)

## 라이선스

프로젝트 라이선스를 따릅니다.
