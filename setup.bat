@echo off
:: Ensure the script runs in the same directory as the .bat file
cd /d "%~dp0"

:: Launch the PowerShell setup script with ExecutionPolicy Bypass
powershell.exe -ExecutionPolicy Bypass -File "setup.ps1"

