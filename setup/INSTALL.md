# Qlog-Stats - Installationsanleitung

Diese Anleitung beschreibt die Installation von Qlog-Stats auf einem neuen PC.

## Automatische Installation (empfohlen)

### Linux / macOS

```bash
# 1. Repository klonen
git clone <repository-url> Qlog-Stats
cd Qlog-Stats

# 2. Setup-Script ausführbar machen und ausführen
chmod +x setup/setup.sh
./setup/setup.sh
```

Das Script führt automatisch folgende Schritte aus:
- Prüft Python 3.8+ Installation
- Prüft Tkinter Verfügbarkeit
- Erstellt Virtual Environment
- Installiert alle Abhängigkeiten (matplotlib)
- Macht run.sh ausführbar

### Windows

```cmd
REM 1. Repository klonen
git clone <repository-url> Qlog-Stats
cd Qlog-Stats

REM 2. Setup-Script ausführen
setup\setup.bat
```

Das Script führt automatisch folgende Schritte aus:
- Prüft Python 3.8+ Installation
- Prüft Tkinter Verfügbarkeit
- Erstellt Virtual Environment
- Installiert alle Abhängigkeiten (matplotlib)
- Erstellt run.bat falls nicht vorhanden

## Manuelle Installation

Falls die automatischen Scripts nicht funktionieren, können Sie folgende Schritte manuell durchführen:

### Voraussetzungen

#### Linux

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk git
```

**Fedora/RHEL:**
```bash
sudo dnf install python3 python3-pip python3-tkinter git
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip tk git
```

#### macOS

```bash
# Mit Homebrew
brew install python3 tcl-tk git
```

#### Windows

1. Python 3.8+ von [python.org](https://www.python.org) herunterladen
2. Bei der Installation "Add Python to PATH" aktivieren
3. Tkinter ist normalerweise bereits enthalten
4. Git von [git-scm.com](https://git-scm.com) installieren

### Installations-Schritte

1. **Repository klonen**
   ```bash
   git clone <repository-url> Qlog-Stats
   cd Qlog-Stats
   ```

2. **Virtual Environment erstellen**

   Linux/macOS:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   Windows:
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate.bat
   ```

3. **Dependencies installieren**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start-Script ausführbar machen** (nur Linux/macOS)
   ```bash
   chmod +x setup/run.sh
   ```

## Installation ohne Git

Falls Git nicht verfügbar ist:

1. Projekt als ZIP herunterladen und entpacken
2. Terminal/Kommandozeile im Projektverzeichnis öffnen
3. Setup-Script ausführen (siehe oben)

Oder manuelle Installation ab Schritt 2 durchführen.

## Programm starten

### Linux / macOS

```bash
# Mit run.sh (empfohlen)
./setup/run.sh

# Oder manuell
source .venv/bin/activate
python3 main.py
```

### Windows

```cmd
REM Mit run.bat (empfohlen)
run.bat

REM Oder manuell
.venv\Scripts\activate.bat
python main.py
```

## Erste Konfiguration

Beim ersten Start muss der Pfad zur Qlog-Datenbank konfiguriert werden:

1. Programm starten
2. Menü: **Datei → Datenbank-Pfad ändern**
3. Pfad zur `qlog.db` Datei angeben

**Standard-Pfade:**
- Linux: `~/.local/share/hamradio/QLog/qlog.db`
- Windows: `C:\Users\<Username>\AppData\Local\hamradio\QLog\qlog.db`
- macOS: `~/Library/Application Support/hamradio/QLog/qlog.db`

Die Konfiguration wird in `config.ini` gespeichert.

## Fehlerbehebung

### "Tkinter nicht gefunden"

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

**Windows:**
Python neu installieren und sicherstellen, dass "tcl/tk and IDLE" aktiviert ist.

### "Virtual Environment kann nicht erstellt werden"

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install python3-venv
```

### "matplotlib Installation schlägt fehl"

Stellen Sie sicher, dass pip aktuell ist:
```bash
python3 -m pip install --upgrade pip
pip install --upgrade matplotlib
```

### "Datenbank kann nicht geöffnet werden"

1. Prüfen Sie, ob der Pfad zur `qlog.db` korrekt ist
2. Prüfen Sie die Dateiberechtigungen
3. Stellen Sie sicher, dass Qlog die Datenbank erstellt hat

## Deinstallation

```bash
# Virtual Environment und Cache löschen
rm -rf .venv __pycache__ ui/__pycache__ features/__pycache__

# Optional: Konfiguration löschen
rm config.ini

# Projektverzeichnis komplett entfernen
cd ..
rm -rf Qlog-Stats
```

## Aktualisierung

```bash
# Repository aktualisieren
git pull

# Dependencies aktualisieren
source .venv/bin/activate  # bzw. .venv\Scripts\activate.bat auf Windows
pip install --upgrade -r requirements.txt
```

## Support

Bei Problemen:
1. Prüfen Sie die Fehlerausgabe
2. Überprüfen Sie die Systemvoraussetzungen
3. Erstellen Sie ein Issue auf GitHub mit der Fehlermeldung
