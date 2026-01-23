#!/bin/bash

# macOS GUI 앱 실행 스크립트

echo "=== 네이버 블로그 자동화 도구 실행 ==="

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo "가상환경이 없습니다."
    echo ""
    echo "macOS에서 tkinter 오류가 발생하는 경우:"
    echo "  ./setup_macos.sh  (시스템 Python 사용 - 권장)"
    echo ""
    echo "또는:"
    echo "  ./setup.sh"
    exit 1
fi

# 가상환경 활성화
source venv/bin/activate

# GUI 앱 실행 (가상환경의 python 직접 사용)
echo "GUI 애플리케이션 실행 중..."
venv/bin/python app.py
