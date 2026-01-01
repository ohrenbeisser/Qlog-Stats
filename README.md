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
├── app_controller.py            # Haupt-Controller (186 Zeilen)
├── config_manager.py            # INI-Konfiguration
├── database.py                  # SQLite DB-Zugriff (nur lesen)
├── stats_exporter.py            # Export-Funktionen
│
├── ui/                          # UI-Layer
│   ├── __init__.py
│   ├── main_window.py           # Fenster-Layout & Menü
│   ├── table_view.py            # Sortierbare Tabelle
│   └── plot_view.py             # Matplotlib-Integration
│
└── features/                    # Feature-Layer
    ├── __init__.py
    ├── statistics.py            # Vereinheitlichte Statistik-Logik
    ├── date_filter.py           # Datumsfilter
    ├── export_handler.py        # Export-Koordination
    └── qrz_integration.py       # QRZ.com Links
```

## Architektur

Das Projekt folgt einer klaren Schichten-Architektur:

### UI-Layer
- **MainWindow**: Menü, Layout, PanedWindow
- **TableView**: Treeview mit intelligenter Sortierung
- **PlotView**: Matplotlib-Canvas-Verwaltung

### Feature-Layer
- **Statistics**: Zentrale Statistik-Logik (Strategy Pattern)
- **DateFilter**: Filter-UI und Validierung
- **ExportHandler**: CSV/TXT Export-Koordination
- **QRZIntegration**: Browser-Integration

### Data-Layer
- **QlogDatabase**: Read-only SQLite-Zugriff
- **StatsExporter**: Export-Funktionalität
- **ConfigManager**: INI-Datei-Verwaltung

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
./run.sh

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
python3 -m py_compile main.py app_controller.py ui/*.py features/*.py

# Import-Test
python3 -c "from app_controller import QlogStatsApp; print('OK')"
```

## Lizenz

MIT License

## Autor

Entwickelt mit Claude AI (Anthropic)

## Änderungshistorie

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
