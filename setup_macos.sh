#!/bin/bash

# macOS 시스템 Python 사용 가상환경 설정 스크립트

echo "=== macOS 시스템 Python으로 환경 설정 ==="

# 시스템 Python 확인
SYSTEM_PYTHON="/usr/bin/python3"
if [ ! -f "$SYSTEM_PYTHON" ]; then
    echo "오류: 시스템 Python을 찾을 수 없습니다."
    exit 1
fi

echo "시스템 Python 버전: $($SYSTEM_PYTHON --version)"

# tkinter 확인
echo "tkinter 확인 중..."
if $SYSTEM_PYTHON -c "import tkinter" 2>/dev/null; then
    echo "✓ tkinter 사용 가능"
else
    echo "⚠️  tkinter를 사용할 수 없습니다."
    exit 1
fi

# 기존 가상환경 삭제
if [ -d "venv" ]; then
    echo "기존 가상환경 삭제 중..."
    rm -rf venv
fi

# 가상환경 생성
echo "시스템 Python으로 가상환경 생성 중..."
$SYSTEM_PYTHON -m venv venv
echo "가상환경 생성 완료"

# 가상환경 활성화
echo "가상환경 활성화 중..."
source venv/bin/activate

# pip 업그레이드 (가상환경의 python 직접 사용)
echo "pip 업그레이드 중..."
venv/bin/python -m pip install --upgrade pip

# 패키지 설치
echo "필요한 패키지 설치 중..."
venv/bin/pip install -r requirements.txt

echo ""
echo "=== 환경 설정 완료 ==="
echo "가상환경을 활성화하려면 다음 명령어를 실행하세요:"
echo "source venv/bin/activate"
echo ""
echo "GUI 애플리케이션을 실행하려면:"
echo "python app.py"
echo ""
