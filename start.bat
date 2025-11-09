@echo off
echo ====================================
echo   Novel Translator Baslatiiliyor
echo ====================================
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause

