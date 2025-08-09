@echo on
setlocal enabledelayedexpansion

rem === Always run from this file's folder ===
cd /d "%~dp0"

rem === Logging ===
if not exist logs mkdir logs
for /f "tokens=1-3 delims=/: " %%a in ("%date% %time%") do set "STAMP=%%a%%b%%c"
set "LOG=logs\run_%STAMP%.log"
echo [%date% %time%] START > "%LOG%"
echo Writing logs to "%LOG%"

rem === Resolve Python interpreter (prefer venv) ===
set "PY=python"
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  echo [%date% %time%] WARNING: .venv not found, using system Python >> "%LOG%"
)

rem === Helper that stops on error ===
set "FAILED="
call :STEP "%PY% --version"                       || goto :FAIL
call :STEP "%PY% etl\refresh_actuals.py"          || goto :FAIL
call :STEP "%PY% prophet_improved.py"             || goto :FAIL
rem Optional sanity check
call :STEP "%PY% checkcsv.py"                     || goto :FAIL

echo [%date% %time%] SUCCESS >> "%LOG%"
echo DONE. See "%LOG%"
exit /b 0

:STEP
echo === Running %~1
echo [%date% %time%] CMD: %~1 >> "%LOG%"
cmd /c %~1 >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [%date% %time%] FAILED: %~1 >> "%LOG%"
  exit /b 1
) else (
  echo [%date% %time%] OK: %~1 >> "%LOG%"
  exit /b 0
)

:FAIL
echo [%date% %time%] ABORTED. See "%LOG%" for details.
exit /b 1
