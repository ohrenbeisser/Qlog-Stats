@echo off
REM Qlog-Stats Installation Script für Windows
REM Dieses Script richtet Qlog-Stats auf einem neuen Windows-PC ein

echo ==========================================
echo   Qlog-Stats Installation (Windows)
echo ==========================================
echo.

REM 1. Python Version prüfen
echo [INFO] Pruefe Python Installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python ist nicht installiert!
    echo Bitte installiere Python 3.8 oder hoeher von https://www.python.org
    echo Wichtig: Bei der Installation "Add Python to PATH" aktivieren!
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python Version: %PYTHON_VERSION%

REM 2. pip prüfen
echo [INFO] Pruefe pip Installation...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] pip ist nicht installiert!
    echo Versuche pip zu installieren...
    python -m ensurepip --default-pip
    if errorlevel 1 (
        echo [FEHLER] pip konnte nicht installiert werden
        pause
        exit /b 1
    )
)
echo [INFO] pip ist installiert

REM 3. Tkinter prüfen
echo [INFO] Pruefe Tkinter Installation...
python -c "import tkinter" 2>nul
if errorlevel 1 (
    echo [WARNUNG] Tkinter ist nicht verfuegbar!
    echo Tkinter sollte mit Python installiert sein.
    echo Falls das Programm nicht startet, installiere Python neu mit Tkinter-Support.
) else (
    echo [INFO] Tkinter ist installiert
)

echo.
echo [INFO] Alle Voraussetzungen erfuellt!
echo.

REM 4. Virtual Environment erstellen
if exist ".venv\" (
    echo [WARNUNG] Virtual Environment existiert bereits
    set /p RECREATE="Moechten Sie es neu erstellen? (j/N): "
    if /i "%RECREATE%"=="j" (
        echo [INFO] Loesche altes Virtual Environment...
        rmdir /s /q .venv
        echo [INFO] Erstelle neues Virtual Environment...
        python -m venv .venv
    )
) else (
    echo [INFO] Erstelle Virtual Environment...
    python -m venv .venv
)

REM 5. Virtual Environment aktivieren
echo [INFO] Aktiviere Virtual Environment...
call .venv\Scripts\activate.bat

REM 6. pip aktualisieren
echo [INFO] Aktualisiere pip...
python -m pip install --upgrade pip

REM 7. Dependencies installieren
echo [INFO] Installiere Abhaengigkeiten...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo [INFO] Alle Abhaengigkeiten wurden installiert
) else (
    echo [FEHLER] requirements.txt nicht gefunden!
    pause
    exit /b 1
)

REM 8. Überprüfe Installation
echo [INFO] Ueberpruefe Installation...
python -c "import matplotlib" 2>nul
if errorlevel 1 (
    echo [FEHLER] matplotlib konnte nicht importiert werden
    pause
    exit /b 1
) else (
    echo [INFO] matplotlib erfolgreich installiert
)

REM 9. Konfiguration
echo.
echo [INFO] Installation abgeschlossen!
echo.

if not exist "config.ini" (
    echo [WARNUNG] config.ini wurde nicht gefunden
    echo [INFO] Eine Beispiel-Konfiguration wird beim ersten Start erstellt
) else (
    echo [INFO] config.ini gefunden
)

REM 10. Start-Batch erstellen falls nicht vorhanden
if not exist "run.bat" (
    echo [INFO] Erstelle run.bat...
    (
        echo @echo off
        echo REM Start-Script fuer Qlog-Stats
        echo.
        echo REM Virtual Environment aktivieren
        echo call .venv\Scripts\activate.bat
        echo.
        echo REM Programm starten
        echo python main.py
        echo.
        echo REM Virtual Environment deaktivieren
        echo deactivate
        echo.
        echo pause
    ) > run.bat
    echo [INFO] run.bat wurde erstellt
)

REM Abschluss
echo.
echo ==========================================
echo   Installation erfolgreich!
echo ==========================================
echo.
echo Um Qlog-Stats zu starten, verwenden Sie:
echo   run.bat
echo.
echo Oder manuell:
echo   .venv\Scripts\activate.bat
echo   python main.py
echo.
echo Beim ersten Start:
echo   1. Programm starten
echo   2. Datei -^> Datenbank-Pfad aendern
echo   3. Pfad zur qlog.db Datei angeben
echo.
pause
