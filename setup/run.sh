#!/bin/bash
# Start-Skript für Qlog-Stats

# Wechsle ins Projekt-Verzeichnis (ein Verzeichnis nach oben)
cd "$(dirname "$0")/.." || exit 1

# Virtual Environment aktivieren
source .venv/bin/activate

# Programm starten
python3 main.py

# Virtual Environment deaktivieren
deactivate
