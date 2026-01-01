# Qlog-Stats

Statistik-Auswertung für Qlog (Amateurfunk-Logbuch)

## Beschreibung

Qlog-Stats ist ein Python-Programm zur Auswertung und Visualisierung von QSO-Daten aus der Qlog-Datenbank.

## Features

- QSO-Statistiken nach:
  - Ländern (DXCC)
  - Bändern
  - Betriebsarten (Modes)
  - Jahren
- Export als CSV und TXT
- Grafische Darstellung mit matplotlib
- Konfigurierbare Datenbankpfade

## Installation

1. Virtual Environment erstellen und aktivieren:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# oder
.venv\Scripts\activate  # Windows
```

2. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

## Verwendung

1. Programm starten:
```bash
python main.py
```

2. Beim ersten Start wird eine Konfigurationsdatei `config.ini` erstellt
3. Falls nötig, Datenbank-Pfad unter "Datei -> Datenbank-Pfad ändern" anpassen

## Konfiguration

Die Konfigurationsdatei `config.ini` enthält:
- Pfad zur Qlog-Datenbank
- Export-Verzeichnis
- GUI-Einstellungen

Standard-Datenbank-Pfad: `~/.local/share/hamradio/QLog/qlog.db`

## Hinweise

- Die Qlog-Datenbank wird nur lesend geöffnet (read-only)
- Exports werden im konfigurierten Export-Verzeichnis gespeichert
- Für Diagramme wird matplotlib benötigt

## Systemanforderungen

- Python 3.7 oder höher
- Tkinter (meist in Python enthalten)
- matplotlib (wird installiert)
