@echo off
echo ====================================
echo ttiglemoa 프로젝트 환경 설정
echo ====================================
echo.

echo [1/3] UV 가상환경 생성...
uv venv

echo.
echo [2/3] 의존성 설치...
uv pip install -r requirements.txt

echo.
echo [3/3] 완료!
echo.
echo 가상환경 활성화: .venv\Scripts\activate
echo Django 서버 실행: python manage.py runserver
echo.
pause
