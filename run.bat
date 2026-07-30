@echo off
set CAPCUT_LAB=%~dp0..\data
python "%~dp0pipeline\cli.py" %*
