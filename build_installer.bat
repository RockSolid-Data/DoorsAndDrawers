@echo off
setlocal

echo ========================================
echo  Doors and Drawers - Build Script
echo  (cx_Freeze + MSI installer)
echo ========================================
echo.

set CMD=%1
if "%CMD%"=="" set CMD=help

if /I "%CMD%"=="freeze" goto :freeze
if /I "%CMD%"=="msi"    goto :msi
if /I "%CMD%"=="test"   goto :test
if /I "%CMD%"=="clean"  goto :clean
if /I "%CMD%"=="all"    goto :all
goto :help

:: -------------------------------------------------------
:: FREEZE – build standalone exe
:: -------------------------------------------------------
:freeze
echo [1/3] Collecting static files ...
python manage.py collectstatic --noinput
if %errorlevel% neq 0 (
    echo ERROR: collectstatic failed
    exit /b 1
)

echo [2/3] Building standalone executable (cx_Freeze) ...
python setup_cx_freeze.py build_exe
if %errorlevel% neq 0 (
    echo ERROR: cx_Freeze build failed
    exit /b 1
)

echo [3/3] Build complete.
echo.
echo   Output folder: build\exe.win-amd64-*\
echo   GUI exe:       DoorsAndDrawers.exe
echo   Debug exe:     DoorsAndDrawers_Debug.exe
echo.
goto :eof

:: -------------------------------------------------------
:: MSI – build Windows MSI installer
:: -------------------------------------------------------
:msi
echo [1/3] Collecting static files ...
python manage.py collectstatic --noinput
if %errorlevel% neq 0 (
    echo ERROR: collectstatic failed
    exit /b 1
)

echo [2/3] Building MSI installer ...
python setup_cx_freeze.py bdist_msi
if %errorlevel% neq 0 (
    echo ERROR: MSI build failed
    exit /b 1
)

echo [3/3] MSI build complete.
echo.
echo   Output: dist\*.msi
echo.
goto :eof

:: -------------------------------------------------------
:: TEST – run the app locally (unfrozen) through launcher
:: -------------------------------------------------------
:test
echo Running application locally via launcher.py ...
echo (Ctrl+C to stop)
echo.
python launcher.py
goto :eof

:: -------------------------------------------------------
:: ALL – freeze then build MSI
:: -------------------------------------------------------
:all
call :freeze
if %errorlevel% neq 0 exit /b 1
call :msi
goto :eof

:: -------------------------------------------------------
:: CLEAN – remove build artifacts
:: -------------------------------------------------------
:clean
echo Cleaning build artifacts ...
if exist build       rmdir /s /q build
if exist dist        rmdir /s /q dist
if exist staticfiles rmdir /s /q staticfiles
echo Done.
goto :eof

:: -------------------------------------------------------
:: HELP
:: -------------------------------------------------------
:help
echo Usage: build_installer.bat [command]
echo.
echo Commands:
echo   freeze   Build standalone .exe (output in build\)
echo   msi      Build Windows MSI installer (output in dist\)
echo   test     Run the app locally with launcher.py
echo   all      Run freeze + msi
echo   clean    Remove build\, dist\, and staticfiles\ directories
echo.
goto :eof
