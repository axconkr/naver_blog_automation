@echo off
REM Windows GUI 앱 실행 스크립트

echo === 네이버 블로그 자동화 도구 실행 ===

REM 가상환경 확인
if not exist "venv" (
    echo 가상환경이 없습니다. setup.bat를 먼저 실행하세요.
    pause
    exit /b 1
)

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM GUI 앱 실행
echo GUI 애플리케이션 실행 중...
python app.py

pause
