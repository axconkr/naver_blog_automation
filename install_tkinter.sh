#!/bin/bash

# macOS에서 tkinter 설치 스크립트

echo "=== macOS tkinter 설치 ==="

# Homebrew가 설치되어 있는지 확인
if ! command -v brew &> /dev/null; then
    echo "오류: Homebrew가 설치되어 있지 않습니다."
    echo "Homebrew 설치: https://brew.sh"
    exit 1
fi

echo "Homebrew로 python-tk 설치 중..."
brew install python-tk

echo ""
echo "설치 완료!"
echo ""
echo "이제 가상환경을 다시 생성하세요:"
echo "rm -rf venv"
echo "./setup.sh"
echo ""
