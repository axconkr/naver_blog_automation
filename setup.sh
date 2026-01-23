#!/bin/bash

# macOS/Linux 가상환경 설정 스크립트

echo "=== 네이버 블로그 자동화 도구 환경 설정 ==="

# Python 버전 확인
if ! command -v python3 &> /dev/null; then
    echo "오류: Python3가 설치되어 있지 않습니다."
    exit 1
fi

# macOS에서 시스템 Python 우선 사용 (tkinter 지원)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # 시스템 Python 경로 확인
    SYSTEM_PYTHON="/usr/bin/python3"
    if [ -f "$SYSTEM_PYTHON" ]; then
        PYTHON_CMD="$SYSTEM_PYTHON"
        echo "macOS 감지: 시스템 Python 사용"
    else
        PYTHON_CMD="python3"
        echo "시스템 Python을 찾을 수 없습니다. 기본 python3 사용"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Python 버전: $($PYTHON_CMD --version)"

# tkinter 확인
echo "tkinter 확인 중..."
if $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
    echo "✓ tkinter 사용 가능"
else
    echo "⚠️  tkinter를 사용할 수 없습니다."
    echo ""
    echo "해결 방법:"
    echo "1. Homebrew로 python-tk 설치:"
    echo "   brew install python-tk"
    echo ""
    echo "2. 또는 시스템 Python 사용 (권장):"
    echo "   /usr/bin/python3 -m venv venv"
    echo ""
    read -p "계속하시겠습니까? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 가상환경 생성
if [ ! -d "venv" ]; then
    echo "가상환경 생성 중..."
    $PYTHON_CMD -m venv venv
    echo "가상환경 생성 완료"
else
    echo "가상환경이 이미 존재합니다."
fi

# 가상환경 활성화
echo "가상환경 활성화 중..."
source venv/bin/activate

# pip 업그레이드
echo "pip 업그레이드 중..."
pip install --upgrade pip

# 패키지 설치
echo "필요한 패키지 설치 중..."
pip install -r requirements.txt

echo ""
echo "=== 환경 설정 완료 ==="
echo "가상환경을 활성화하려면 다음 명령어를 실행하세요:"
echo "source venv/bin/activate"
echo ""
echo "GUI 애플리케이션을 실행하려면:"
echo "python app.py"
echo ""
