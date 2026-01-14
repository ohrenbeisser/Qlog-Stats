# Qlog-Stats

Statistik-Auswertungs-Tool für Qlog (Amateur Radio Logging Software)

## Übersicht

Qlog-Stats ist ein Python-basiertes Desktop-Tool zur Analyse und Visualisierung von QSO-Daten aus der Qlog-Datenbank. Es bietet sortierbare Tabellen, Diagramme und Export-Funktionen für verschiedene Statistik-Ansichten.

## Features

- **Statistik-Anzeigen**
  - QSOs nach Ländern (Top 20)
  - QSOs nach Bändern
  - QSOs nach Modes
  - QSOs nach Jahren
  - Sonderrufzeichen-Erkennung (Deutsche Stationen)

- **Interaktive Funktionen**
  - Sortierbare Tabellen (Klick auf Spalten-Header)
  - Datumsfilter mit Bereichsauswahl
  - Matplotlib-Diagramme
  - QRZ.com Integration (Doppelklick auf Rufzeichen)

- **Export**
  - CSV-Format
  - Formatiertes TXT-Format mit Zeitstempel

## Projekt-Struktur

```
Qlog-Stats/
├── main.py                      # Einstiegspunkt (19 Zeilen)
├── app_controller.py            # Haupt-Controller (506 Zeilen)
├── config.ini                   # Konfigurationsdatei
│
├── core/                        # Core-Layer (Daten & Konfiguration)
│   ├── __init__.py
│   ├── database.py              # SQLite DB-Zugriff (nur lesen)
│   ├── config_manager.py        # INI-Konfiguration
│   └── stats_exporter.py        # Export-Funktionen
│
├── ui/                          # UI-Layer
│   ├── __init__.py
│   ├── main_window.py           # Fenster-Layout & Menü
│   ├── table_view.py            # Sortierbare Tabelle
│   ├── plot_view.py             # Matplotlib-Integration
│   ├── settings_dialog.py       # Einstellungs-Dialog
│   └── table_columns.py         # Spalten-Definitionen
│
├── features/                    # Feature-Layer
│   ├── __init__.py
│   ├── statistics.py            # Vereinheitlichte Statistik-Logik
│   ├── date_filter.py           # Datumsfilter
│   ├── export_handler.py        # Export-Koordination
│   ├── context_menu.py          # Kontextmenü & Detail-Dialog
│   ├── query_builder.py         # SQL-Query-Builder
│   ├── query_manager.py         # Query-Verwaltung
│   ├── query_manager_dialog.py  # Query-Manager UI
│   └── qrz_integration.py       # QRZ.com Links
│
└── setup/                       # Setup & Installation
    ├── setup.sh                 # Linux/macOS Setup-Script
    ├── setup.bat                # Windows Setup-Script
    ├── run.sh                   # Start-Script
    └── INSTALL.md               # Detaillierte Installationsanleitung
```

## Architektur

Das Projekt folgt einer klaren Schichten-Architektur:

### Core-Layer (Daten & Konfiguration)
- **QlogDatabase**: Read-only SQLite-Zugriff auf Qlog-Datenbank
- **ConfigManager**: INI-Datei-Verwaltung und Einstellungen
- **StatsExporter**: Export-Funktionalität für CSV/TXT

### UI-Layer (Benutzeroberfläche)
- **MainWindow**: Hauptfenster mit Menü, Layout und PanedWindow
- **TableView**: Treeview mit intelligenter Sortierung
- **PlotView**: Matplotlib-Canvas-Verwaltung
- **SettingsDialog**: Einstellungs-Dialog für Konfiguration
- **table_columns**: Spalten-Definitionen für Detail-Tabellen

### Feature-Layer (Business-Logik)
- **Statistics**: Zentrale Statistik-Logik (Strategy Pattern)
- **DateFilter**: Filter-UI und Validierung
- **ExportHandler**: CSV/TXT Export-Koordination
- **ContextMenu**: Kontextmenü und Detail-Dialog
- **QueryBuilder**: SQL-Query-Builder-Dialog
- **QueryManager**: Verwaltung benutzerdefinierter Queries
- **QueryManagerDialog**: UI für Query-Verwaltung
- **QRZIntegration**: Browser-Integration für QRZ.com

## Installation

### Voraussetzungen

- Python 3.8+
- Tkinter (meist mit Python installiert)
- Matplotlib

### Setup

```bash
# Virtual Environment erstellen
python3 -m venv .venv

# Aktivieren
source .venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

### Konfiguration

Die Datenbank-Pfad-Konfiguration erfolgt beim ersten Start über:
**Datei → Datenbank-Pfad ändern**

Standard-Pfad: `~/.local/share/hamradio/QLog/qlog.db`

Alternativ kann `config.ini` manuell bearbeitet werden:

```ini
[Database]
path = /home/user/.local/share/hamradio/QLog/qlog.db

[Export]
directory = ./exports

[Window]
width = 1200
height = 700
```

## Verwendung

```bash
# Mit run.sh (empfohlen)
./setup/run.sh

# Oder direkt
source .venv/bin/activate
python3 main.py
```

### Bedienung

1. **Statistik auswählen**: Menü → Statistik → [Typ wählen]
2. **Datumsfilter**: Von/Bis Datum eingeben → "Filter anwenden"
3. **Sortieren**: Klick auf Spalten-Header (▲/▼ zeigt Sortierung)
4. **QRZ-Link**: Doppelklick auf Rufzeichen (bei Sonderrufzeichen)
5. **Export**: Menü → Export → CSV/TXT

## Sonderrufzeichen-Erkennung

Deutsche Sonderrufzeichen werden erkannt durch:
- DR-Präfix (Event-Stationen)
- D*0-Präfix (Klubstationen: DL0, DA0, DF0, etc.)
- Mehrere aufeinanderfolgende Ziffern (DL75DARC, DL2025W, etc.)
- Rufzeichen mit "/" werden ausgeschlossen

## Entwicklung

### Code-Stil
- PEP 8 konforme Formatierung
- Ausführliche Docstrings
- Inline-Kommentare für komplexe Logik
- Type Hints wo sinnvoll

### Refactoring-Historie

**Ursprüngliche Version:**
- main.py: 552 Zeilen monolithischer Code
- 5 fast identische Statistik-Methoden

**Refactored Version:**
- main.py: 19 Zeilen (97% Reduktion!)
- 10 spezialisierte Module
- Vereinheitlichte Statistik-Logik (Strategy Pattern)
- Klare Separation of Concerns

### Tests

```bash
# Syntax-Check
python3 -m py_compile main.py app_controller.py core/*.py ui/*.py features/*.py

# Import-Test
python3 -c "from app_controller import QlogStatsApp; print('OK')"
```

## Lizenz

MIT License

## Autor

Entwickelt mit Claude AI (Anthropic)

## Änderungshistorie

### Version 2.1 (2026-01-14)
- Projekt-Reorganisation und Optimierung
- Neues `core/` Verzeichnis für Datenbank, Config und Export
- `setup/` Verzeichnis für alle Setup- und Installations-Dateien
- Module in logische Verzeichnisse verschoben (query_manager → features, table_columns → ui)
- Entfernung redundanter Backup-Dateien
- Aktualisierte README mit vollständiger Modul-Dokumentation

### Version 2.0 (2026-01-02)
- Komplettes Refactoring in modulare Architektur
- Vereinheitlichte Statistik-Logik
- Verbesserte Dokumentation und Kommentare
- Bugfixes: Callback-Initialisierung, Exception-Handling

### Version 1.0
- Initiale Version mit monolithischem Code
- Basis-Funktionalität: Statistiken, Filter, Export

## Support

Bei Problemen bitte Issue auf GitHub erstellen.
