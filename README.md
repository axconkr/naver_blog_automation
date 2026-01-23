# 네이버 블로그 자동화 도구

네이버 블로그에 자동으로 글을 작성하고 업로드하는 자동화 도구입니다.

## 주요 기능

1. **엑셀 파일 생성**: 블로그 제목이 포함된 엑셀 파일 생성
2. **블로그 본문 생성**: Gemini API를 사용하여 SEO 최적화된 블로그 본문 자동 생성
3. **블로그 업로드**: 생성된 글을 네이버 블로그에 자동 업로드

## 환경 설정

### macOS/Linux

**중요: macOS에서 tkinter 오류가 발생하는 경우**

Homebrew Python을 사용 중이라면 다음 중 하나를 선택하세요:

**방법 1: 시스템 Python 사용 (권장)**
```bash
# 기존 가상환경 삭제
rm -rf venv

# 시스템 Python으로 가상환경 생성
/usr/bin/python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

**방법 2: Homebrew로 python-tk 설치**
```bash
brew install python-tk
./setup.sh
```

1. 가상환경 설정:
```bash
./setup.sh
```

2. 가상환경 활성화:
```bash
source venv/bin/activate
```

3. GUI 앱 실행:
```bash
./run_app.sh
# 또는
python app.py
```

4. macOS 앱 빌드:
```bash
./build_app.sh
```

빌드된 앱은 `dist/네이버블로그자동화.app`에 생성됩니다.

### Windows

1. 가상환경 설정:
```cmd
setup.bat
```

2. 가상환경 활성화:
```cmd
venv\Scripts\activate.bat
```

3. GUI 앱 실행:
```cmd
run_app.bat
# 또는
python app.py
```

4. EXE 파일 빌드:
```cmd
build_exe.bat
```

빌드된 EXE 파일은 `dist\네이버블로그자동화.exe`에 생성됩니다.

## 환경 변수 설정

`.env` 파일에 다음 정보를 설정해야 합니다:

```
NAVER_ID=your_naver_id
NAVER_PW=your_naver_password
GEMINI_API_KEY=your_gemini_api_key
```

## 사용 방법

### GUI 사용

1. `app.py`를 실행하여 GUI 창을 엽니다.
2. 다음 버튼 중 하나를 선택:
   - **1. 엑셀 파일 생성**: 블로그 제목이 포함된 엑셀 파일 생성
   - **2. 블로그 본문 생성**: Gemini API로 블로그 본문 생성
   - **3. 블로그 업로드**: 네이버 블로그에 글 업로드
   - **전체 실행**: 위 3단계를 순차적으로 실행

### 명령줄 사용

각 스크립트를 개별적으로 실행할 수 있습니다:

```bash
# 엑셀 파일 생성
python exel_crete.py

# 블로그 본문 생성
python create.py

# 블로그 업로드
python upload_bot.py
```

## 파일 구조

- `app.py`: GUI 애플리케이션
- `exel_crete.py`: 엑셀 파일 생성 스크립트
- `create.py`: 블로그 본문 생성 스크립트
- `upload_bot.py`: 블로그 업로드 스크립트
- `login.py`: 네이버 로그인 테스트 스크립트
- `gemini.py`: Gemini API 유틸리티
- `.env`: 환경 변수 파일 (민감 정보 포함)
- `requirements.txt`: 필요한 Python 패키지 목록

## 주의사항

1. `.env` 파일은 Git에 커밋하지 마세요. (민감 정보 포함)
2. 네이버 로그인 시 보안 정책(캡차, 2단계 인증 등)에 따라 자동 로그인이 차단될 수 있습니다.
3. Gemini API 사용량에 따라 비용이 발생할 수 있습니다.
4. 블로그 업로드 시 네이버의 정책을 준수하세요.

## 문제 해결

### 가상환경이 활성화되지 않는 경우

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```cmd
venv\Scripts\activate.bat
```

### 패키지 설치 오류

가상환경이 활성화된 상태에서:
```bash
pip install -r requirements.txt
```

### GUI가 실행되지 않는 경우

**macOS에서 `ModuleNotFoundError: No module named '_tkinter'` 오류:**

Homebrew Python을 사용 중이라면 tkinter가 포함되지 않을 수 있습니다.

**해결 방법:**

1. **시스템 Python 사용 (가장 간단):**
```bash
rm -rf venv
/usr/bin/python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

2. **Homebrew로 python-tk 설치:**
```bash
brew install python-tk
```

3. **tkinter 확인:**
```bash
python -m tkinter
```

정상적으로 작동하면 빈 창이 열립니다.

### 빌드 오류

PyInstaller가 제대로 설치되었는지 확인:
```bash
pip install --upgrade pyinstaller
```

## 라이선스

이 프로젝트는 개인 사용 목적으로 제작되었습니다.
