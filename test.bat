@echo off
setlocal

echo =======================================================
echo         CareerCompass AI - Automated Test Runner
echo =======================================================
echo.

if exist "venv\Scripts\activate.bat" (
    echo [*] Using virtual environment...
    call venv\Scripts\activate.bat
)

echo [*] Running automated Python test suite...
echo.

python -m unittest discover -s tests -p "test_*.py" -v

echo.
echo =======================================================
echo  Tests finished!
echo =======================================================
pause
