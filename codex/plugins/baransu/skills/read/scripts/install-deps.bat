@echo off
setlocal

:: Check if markitdown is already installed
py -m markitdown --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "delims=" %%v in ('py -m markitdown --version 2^>nul') do set MKVER=%%v
    echo markitdown OK (%MKVER%)
    exit /b 0
)

:: Try python launcher first, then python
echo Installing markitdown...
py -m pip install markitdown
if %ERRORLEVEL% EQU 0 goto verify

python -m pip install markitdown
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: markitdown installation failed. Check your Python/pip environment.
    exit /b 1
)

:verify
py -m markitdown --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: markitdown installed but not runnable. Check Python PATH.
    exit /b 1
)
echo markitdown installed successfully.
exit /b 0
