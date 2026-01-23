@echo off
REM Windows 가상환경 설정 스크립트

echo === 네이버 블로그 자동화 도구 환경 설정 ===

REM Python 버전 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo 오류: Python이 설치되어 있지 않습니다.
    pause
    exit /b 1
)

echo Python 버전 확인 중...
python --version

REM 가상환경 생성
if not exist "venv" (
    echo 가상환경 생성 중...
    python -m venv venv
    echo 가상환경 생성 완료
) else (
    echo 가상환경이 이미 존재합니다.
)

REM 가상환경 활성화
echo 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM pip 업그레이드
echo pip 업그레이드 중...
python -m pip install --upgrade pip

REM 패키지 설치
echo 필요한 패키지 설치 중...
pip install -r requirements.txt

echo.
echo === 환경 설정 완료 ===
echo 가상환경을 활성화하려면 다음 명령어를 실행하세요:
echo venv\Scripts\activate.bat
echo.
echo GUI 애플리케이션을 실행하려면:
echo python app.py
echo.

pause
