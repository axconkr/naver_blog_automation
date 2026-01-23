@echo off
REM Windows EXE 빌드 스크립트

echo === Windows EXE 빌드 시작 ===

REM 가상환경 확인
if not exist "venv" (
    echo 오류: 가상환경이 없습니다. setup.bat를 먼저 실행하세요.
    pause
    exit /b 1
)

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM PyInstaller 설치 확인
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller 설치 중...
    pip install pyinstaller
)

REM 빌드 디렉토리 정리
if exist "dist" (
    echo 기존 빌드 파일 삭제 중...
    rmdir /s /q dist
)

if exist "build" (
    echo 기존 빌드 파일 삭제 중...
    rmdir /s /q build
)

REM .env 파일 확인
if not exist ".env" (
    echo 경고: .env 파일이 없습니다. 빌드는 계속되지만 실행 시 오류가 발생할 수 있습니다.
)

REM PyInstaller로 EXE 빌드
echo EXE 빌드 중...
if exist ".env" (
    pyinstaller --name="네이버블로그자동화" ^
        --windowed ^
        --onedir ^
        --icon=NONE ^
        --add-data=".env;." ^
        --add-data="exel_crete.py;." ^
        --add-data="create.py;." ^
        --add-data="upload_bot.py;." ^
        --add-data="gemini.py;." ^
        --hidden-import=selenium ^
        --hidden-import=openpyxl ^
        --hidden-import=dotenv ^
        --hidden-import=pyperclip ^
        --hidden-import=google.generativeai ^
        --hidden-import=tkinter ^
        app.py
) else (
    pyinstaller --name="네이버블로그자동화" ^
        --windowed ^
        --onedir ^
        --icon=NONE ^
        --add-data="exel_crete.py;." ^
        --add-data="create.py;." ^
        --add-data="upload_bot.py;." ^
        --add-data="gemini.py;." ^
        --hidden-import=selenium ^
        --hidden-import=openpyxl ^
        --hidden-import=dotenv ^
        --hidden-import=pyperclip ^
        --hidden-import=google.generativeai ^
        --hidden-import=tkinter ^
        app.py
)

if %errorlevel% equ 0 (
    echo.
    echo === 빌드 완료 ===
    echo 실행 파일 위치: dist\네이버블로그자동화\네이버블로그자동화.exe
    echo.
) else (
    echo 빌드 실패
    pause
    exit /b 1
)

pause
