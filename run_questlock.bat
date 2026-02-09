@echo off
chcp 65001 >nul
title QuestLock v1.0.0 - Created by Dangel
color 0C

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║              🔒 QuestLock v1.0.0 🔒                      ║
echo ║                Created by Dangel                         ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되지 않았거나 PATH에 추가되지 않았습니다.
    echo Python 3.8 이상을 설치해주세요.
    echo.
    pause
    exit /b 1
)

echo [확인] Python 설치됨
python --version

REM QuestLock 폴더 찾기
set QUESTLOCK_DIR=
set FOUND_FOLDER=

REM 현재 폴더에 main.py가 있는지 확인 (QuestLock 폴더 자체에서 실행)
if exist "%~dp0main.py" (
    set QUESTLOCK_DIR=%~dp0
    set FOUND_FOLDER=현재 폴더
    echo [확인] QuestLock 프로그램 발견: %~dp0
) else if exist "%~dp0QuestLock\main.py" (
    set QUESTLOCK_DIR=%~dp0QuestLock
    set FOUND_FOLDER=QuestLock
    echo [확인] QuestLock 폴더 발견: %~dp0QuestLock
) else if exist "%~dp0game_ransomware_simulator\main.py" (
    set QUESTLOCK_DIR=%~dp0game_ransomware_simulator
    set FOUND_FOLDER=game_ransomware_simulator
    echo [확인] game_ransomware_simulator 폴더 발견: %~dp0game_ransomware_simulator
) else (
    echo [오류] QuestLock 프로그램을 찾을 수 없습니다.
    echo 현재 위치: %~dp0
    echo.
    echo 다음을 확인해주세요:
    echo 1. main.py 파일이 있는지 확인
    echo 2. 폴더 구조가 올바른지 확인
    echo.
    pause
    exit /b 1
)

REM 의존성 설치
echo.
echo [진행] 필요한 라이브러리를 확인하고 설치합니다...
pip install -r "%QUESTLOCK_DIR%\requirements.txt" >nul 2>&1

if errorlevel 1 (
    echo [오류] 의존성 설치에 실패했습니다.
    echo 다음 명령어를 직접 실행해보세요:
    echo pip install -r "%QUESTLOCK_DIR%\requirements.txt"
    echo.
    pause
    exit /b 1
)

echo [완료] 라이브러리 설치 완료

REM 프로그램 실행
echo.
echo ════════════════════════════════════════════════════════════
echo  프로그램을 시작합니다...
echo ════════════════════════════════════════════════════════════
echo.

REM 배치 파일이 있는 디렉토리로 이동
cd /d "%~dp0"

REM 폴더 구조에 따라 적절한 모듈 실행
if "%FOUND_FOLDER%"=="현재 폴더" (
    REM 현재 폴더가 QuestLock 폴더인 경우
    cd ..
    python -m QuestLock.main
) else if "%FOUND_FOLDER%"=="QuestLock" (
    python -m QuestLock.main
) else if "%FOUND_FOLDER%"=="game_ransomware_simulator" (
    python -m game_ransomware_simulator.main
) else (
    echo [오류] 실행할 모듈을 찾을 수 없습니다.
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════
echo  프로그램이 종료되었습니다.
echo ════════════════════════════════════════════════════════════
pause
