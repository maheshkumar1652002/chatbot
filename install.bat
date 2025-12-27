@echo off

REM Try to run ollama to confirm installation

powershell -Command "ollama" >nul 2>&1
set EXITCODE=%ERRORLEVEL%
echo %EXITCODE%

if %EXITCODE%==0 (
    echo Ollama is installed
    exit
) else (
    echo Ollama is NOT installed
    ollama.exe
)

REM Delete the .ollama folder from the user profile

set "OLLAMA_DIR=%USERPROFILE%\.ollama"

if exist "%OLLAMA_DIR%" (
    echo Deleting folder: %OLLAMA_DIR%
    rmdir /s /q "%OLLAMA_DIR%"
    echo Folder deleted.
) else (
    echo No .ollama folder found.
)

pause

set "MY_OLLAMA=%cd%\.ollama"


REM Copy your working directory's .ollama to default location
echo Copying .ollama from %MY_OLLAMA% to %OLLAMA_DIR%...
xcopy "%MY_OLLAMA%" "%OLLAMA_DIR%" /E /I /H /Y

pause
