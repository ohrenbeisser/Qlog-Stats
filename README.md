# Qlog-Stats - QSO Statistik Auswertung

**Statistik- und Analyse-Tool für QLog (Amateur Radio Logging)**

Qlog-Stats ist eine Desktop-Anwendung zur übersichtlichen Auswertung Ihrer QSO-Daten aus QLog. Mit umfangreichen Statistiken, interaktiven Diagrammen und flexiblen Export-Funktionen behalten Sie den Überblick über Ihre Funkaktivitäten.

---

## Funktionsübersicht

### Statistiken & Auswertungen
- **Länder-Statistik** - Welche Länder Sie gearbeitet haben (Top 20 mit Diagramm)
- **Band-Statistik** - Aktivität auf allen Amateurfunk-Bändern
- **Mode-Statistik** - Betriebsarten-Auswertung (SSB, CW, FT8, etc.)
- **Zeit-Statistiken** - Nach Jahr, Monat, Wochentag, Tag, Stunde
- **Propagations-Daten** - K-Index, A-Index und SFI im Zeitverlauf
- **Top/Flop QSO-Tage** - Ihre aktivsten und ruhigsten Tage
- **Rufzeichen-Statistik** - Häufig gearbeitete Stationen
- **Sonderrufzeichen** - Automatische Erkennung von Event-Stationen

### QSL-Verwaltung
- Versendete und empfangene Karten
- Angeforderte und zu versendende Karten
- LotW-Bestätigungen (Logbook of The World)
- eQSL-Bestätigungen

### Suche & Filter
- **Rufzeichen-Suche** - Schnelle Suche nach bestimmten Calls
- **Datum-Filter** - Zeitraum einschränken mit Schnellauswahl
- **Band/Mode/Land-Filter** - Kombinierbare Filter
- **Benutzerdefinierte Abfragen** - SQL-Query-Builder für individuelle Auswertungen

### Darstellung
- **Modernes Design** - Azure Theme in Hell/Dunkel-Modus
- **Interaktive Diagramme** - Balken- und Liniendiagramme
- **Sortierbare Tabellen** - Klick auf Spaltenköpfe zum Sortieren
- **Anpassbare Spalten** - Wählen Sie, welche Daten angezeigt werden

### Export & Integration
- **CSV-Export** - Für Excel, LibreOffice Calc
- **TXT-Export** - Formatierte Textdatei
- **QRZ.com** - Rechtsklick öffnet QRZ.com Profil
- **Google Maps** - Locator auf Karte anzeigen

---

## Installation

### Voraussetzungen
- Python 3.8 oder höher
- QLog installiert mit vorhandener Datenbank

### Linux / macOS
```bash
cd /pfad/zu/Qlog-Stats
./setup/setup.sh
./setup/run.sh
```

### Windows
```cmd
cd C:\Pfad\zu\Qlog-Stats
setup\setup.bat
python main.py
```

### Manuell
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python3 main.py
```

---

## Erste Schritte

### 1. Datenbank konfigurieren
Beim ersten Start oder über **Datei → Einstellungen**:
- Qlog-Datenbank-Pfad angeben
- Linux: `~/.local/share/hamradio/QLog/qlog.db`
- Windows: `C:\Users\[Name]\AppData\Local\QLog\qlog.db`

### 2. Theme wählen (optional)
**Datei → Einstellungen → Erscheinungsbild**:
- Theme: Azure (modern) oder Standard
- Modus: Hell oder Dunkel
- Neustart erforderlich nach Änderung

### 3. Filter einstellen
Im Filter-Bereich oben:
- **Von/Bis**: Datum per Hand oder Schnellauswahl
- **Band/Mode/Land**: Einzelne oder kombinierte Filter
- **"Filter anwenden"** klicken

---

## Bedienungsanleitung

### Statistiken anzeigen

Über **Menü → Statistik** die gewünschte Auswertung wählen:

| Statistik | Beschreibung |
|-----------|--------------|
| Länder | QSO-Anzahl pro DXCC-Land mit Balkendiagramm |
| Bänder | Verteilung auf Amateurfunk-Bänder |
| Modes | Betriebsarten-Auswertung |
| Jahre | Aktivität über die Jahre |
| Monate | Monatliche Aktivität |
| Wochentage | An welchen Tagen Sie am aktivsten sind |
| Monatstage | Welcher Tag im Monat am aktivsten |
| Stunden | Tageszeit-Verteilung (UTC) |
| Rufzeichen | Häufig gearbeitete Stationen |
| Top QSO-Tage | Ihre aktivsten Tage |
| Flop QSO-Tage | Tage mit den wenigsten QSOs |
| Propagation | K-Index, A-Index, SFI im Zeitverlauf |

**Tipp:** Doppelklick auf eine Zeile zeigt alle QSOs für diesen Eintrag.

### Rufzeichen suchen

**Rufzeichen → Suche** oder direkt über das Suchfeld:
1. Rufzeichen eingeben (vollständig oder teilweise)
2. **Teilstring**: Sucht überall im Callsign
3. **Beginnend**: Sucht nur am Anfang
4. Automatische Suche bei Eingabe

**Sonderrufzeichen** (Menü: Rufzeichen → Sonderrufzeichen):
- Zeigt Event-Stationen, Sonder-DOKs, Jubiläums-Rufzeichen
- Erkennt automatisch ungewöhnliche Rufzeichen-Strukturen

### QSL-Übersicht

**Menü → QSL** für verschiedene QSL-Ansichten:

| Ansicht | Zeigt |
|---------|-------|
| Karte versendet | QSLs die Sie verschickt haben |
| Karte erhalten | Empfangene QSL-Bestätigungen |
| Karte angefordert | Ausstehende Anfragen |
| Karte zu versenden | In der Warteschlange |
| LotW erhalten | Logbook of The World Bestätigungen |
| eQSL erhalten | Elektronische QSLs |

### Rechtsklick-Menü

Rechtsklick auf eine Tabellenzeile öffnet Optionen:
- **Details** - Zeigt alle QSO-Informationen
- **QRZ.com öffnen** - Öffnet QRZ.com Profil im Browser
- **Grid auf Karte** - Zeigt Locator auf Google Maps

### Benutzerdefinierte Abfragen

**Menü → Abfragen → Neue Abfrage**:
1. Bedingungen hinzufügen (Feld, Operator, Wert)
2. AND/OR Verknüpfung wählen
3. Anzuzeigende Spalten auswählen
4. SQL-Vorschau prüfen
5. Abfrage speichern

Gespeicherte Abfragen erscheinen direkt im Abfragen-Menü.

### Daten exportieren

**Menü → Export**:
- **Als CSV** - Für Tabellenkalkulation
- **Als TXT** - Formatierte Textdatei

Exportiert werden die aktuell sichtbaren Daten mit aktiven Filtern.

---

## Filter verwenden

### Datumsfilter
- **Von/Bis**: Manuell eingeben (Format: JJJJ-MM-TT)
- **Schnellauswahl**: Buttons für Jahr, Monat, Woche, Tag
- Der aktuell ausgewählte Zeitraum wird angezeigt

### Band/Mode/Land-Filter
- **Alle**: Kein Filter aktiv
- Wählen Sie einen spezifischen Wert aus der Dropdown-Liste
- Filter können kombiniert werden

### Filter anwenden
- Klicken Sie auf **"Filter anwenden"** oder drücken Sie Enter
- Die Anzahl der gefundenen QSOs wird angezeigt
- **"Zurücksetzen"** setzt alle Filter auf den gesamten Zeitraum

---

## Einstellungen

**Datei → Einstellungen** öffnet den Konfigurations-Dialog:

### Datenbank
- Pfad zur QLog-Datenbank (qlog.db)

### Export
- Zielverzeichnis für CSV/TXT-Exporte

### Erscheinungsbild
- **Theme**: Azure (empfohlen) oder Standard
- **Modus**: Hell oder Dunkel
- Neustart erforderlich nach Änderung

### Spalten
- Auswahl der Spalten für Detail-Tabellen
- Rufzeichen ist immer sichtbar

---

## Tipps & Tricks

### Effiziente Filter-Nutzung
- Kombinieren Sie Datum + Band + Mode für präzise Auswertungen
- Schnellauswahl-Buttons sparen Zeit bei häufigen Zeiträumen
- Die QSO-Anzahl hilft bei der Kontrolle der Filter

### Tabellen sortieren
- Klick auf Spalten-Header sortiert auf-/absteigend
- Symbol ▲ (aufsteigend) oder ▼ (absteigend) zeigt Sortierung
- Funktioniert bei allen Tabellen

### Diagramme anpassen
- Trenner zwischen Tabelle und Diagramm verschieben
- Propagations-Diagramm hat zwei Y-Achsen
- Diagramme passen sich automatisch an

### Große Datenbanken
- Bei >50.000 QSOs: Filter verwenden für bessere Performance
- Datumsbereich einschränken beschleunigt die Anzeige

---

## Fehlerbehebung

### "Datenbank nicht gefunden"
→ Pfad in Einstellungen prüfen und korrigieren

### Leere Tabelle trotz QSOs
→ Filter prüfen und ggf. "Zurücksetzen" klicken
→ QSO-Anzahl kontrollieren (rechts neben den Buttons)

### Theme wird nicht korrekt angezeigt
→ Anwendung neu starten nach Theme-Änderung
→ Prüfen ob `themes/`-Verzeichnis vorhanden ist

### Export funktioniert nicht
→ Export-Verzeichnis in Einstellungen prüfen
→ Schreibrechte im Verzeichnis kontrollieren

---

## Changelog

### Version 3.0 (Januar 2026)
- Azure Theme mit Hell/Dunkel-Modus
- Propagations-Statistik (K-Index, A-Index, SFI)
- Sonderrufzeichen-Erkennung
- Optimierte Menüstruktur
- Code-Optimierungen und Vereinheitlichungen

### Version 2.0
- Modulare Architektur
- Benutzerdefinierte SQL-Abfragen
- Verbessertes Filter-System

### Version 1.0
- Erste Version mit Basis-Funktionalität

---

## Lizenz

MIT License - Freie Verwendung, Modifikation und Weitergabe erlaubt.

---

## Links

- **QLog**: https://github.com/foldynl/QLog
- **QRZ.com**: https://www.qrz.com

---

**73 und viel Spaß beim Auswerten Ihrer QSOs!**
