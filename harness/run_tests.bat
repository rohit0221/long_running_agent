@echo off
call .venv\Scripts\activate
set PYTHONPATH=%PYTHONPATH%;%CD%
coverage run -m pytest target_repo/tests
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
coverage xml
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
coverage report -m
exit /b 0
