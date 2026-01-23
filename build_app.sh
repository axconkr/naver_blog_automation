#!/bin/bash

# macOS 앱 빌드 스크립트

echo "=== macOS 앱 빌드 시작 ==="

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo "오류: 가상환경이 없습니다. setup.sh를 먼저 실행하세요."
    exit 1
fi

# 가상환경 활성화
source venv/bin/activate

# PyInstaller 설치 확인
if ! pip show pyinstaller &> /dev/null; then
    echo "PyInstaller 설치 중..."
    pip install pyinstaller
fi

# 빌드 디렉토리 정리
if [ -d "dist" ]; then
    echo "기존 빌드 파일 삭제 중..."
    rm -rf dist
fi

if [ -d "build" ]; then
    echo "기존 빌드 파일 삭제 중..."
    rm -rf build
fi

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo "경고: .env 파일이 없습니다. 빌드는 계속되지만 실행 시 오류가 발생할 수 있습니다."
fi

# PyInstaller로 앱 빌드
echo "앱 빌드 중..."
if [ -f ".env" ]; then
    pyinstaller --name="네이버블로그자동화" \
        --windowed \
        --onedir \
        --icon=NONE \
        --add-data=".env:." \
        --add-data="exel_crete.py:." \
        --add-data="create.py:." \
        --add-data="upload_bot.py:." \
        --add-data="gemini.py:." \
        --hidden-import=selenium \
        --hidden-import=openpyxl \
        --hidden-import=dotenv \
        --hidden-import=pyperclip \
        --hidden-import=google.generativeai \
        --hidden-import=tkinter \
        app.py
else
    pyinstaller --name="네이버블로그자동화" \
        --windowed \
        --onedir \
        --icon=NONE \
        --add-data="exel_crete.py:." \
        --add-data="create.py:." \
        --add-data="upload_bot.py:." \
        --add-data="gemini.py:." \
        --hidden-import=selenium \
        --hidden-import=openpyxl \
        --hidden-import=dotenv \
        --hidden-import=pyperclip \
        --hidden-import=google.generativeai \
        --hidden-import=tkinter \
        app.py
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "=== 빌드 완료 ==="
    echo "앱 위치: dist/네이버블로그자동화/"
    echo ""
    echo "앱을 실행하려면:"
    echo "open dist/네이버블로그자동화/네이버블로그자동화.app"
    echo ""
else
    echo "빌드 실패"
    exit 1
fi
