@echo off
call .venv\Scripts\activate
set PYTHONPATH=%CD%
coverage run -m pytest
if %ERRORLEVEL% EQU 5 (
    echo No tests collected. Generating zero coverage report.
    coverage xml
    exit /b 5
)
if %ERRORLEVEL% NEQ 0 (
    exit /b %ERRORLEVEL%
)
coverage xml
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
coverage report -m
exit /b 0
