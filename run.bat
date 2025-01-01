@echo off
chcp 936 >nul
:loop
cls
echo running main.py...
py main.py

echo.
echo to run main.py again, enter "1" then enter. press any other key to exit
set /p choice=your choice:

if "%choice%"=="1" (
    goto loop
) else (
    echo 程序结束。
    pause
    exit
)