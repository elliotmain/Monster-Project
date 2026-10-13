@echo off
cls
openfiles >nul 2>&1
if '%errorlevel%' NEQ '0' (
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%cd%"
    CD /D "%~dp0"
:--------------------------------------
cls
cd %userprofile%\Monster-Project\Monster-Project-Tools\Offensive-Tools\Monster-DoS-Tool
cls
echo [Monster-Project] - Starting...
python3 STARTER.py
pause
