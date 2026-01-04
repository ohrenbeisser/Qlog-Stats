#!/bin/bash
# Qlog-Stats Installation Script
# Dieses Script richtet Qlog-Stats auf einem neuen PC ein

set -e  # Bei Fehler abbrechen

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Qlog-Stats Installation"
echo "=========================================="
echo ""

# Funktion für farbige Ausgaben
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNUNG]${NC} $1"
}

print_error() {
    echo -e "${RED}[FEHLER]${NC} $1"
}

# 1. Python Version prüfen
print_info "Prüfe Python Installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 ist nicht installiert!"
    echo "Bitte installiere Python 3.8 oder höher:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv python3-tk"
    echo "  Fedora/RHEL:   sudo dnf install python3 python3-pip python3-tkinter"
    echo "  Arch:          sudo pacman -S python python-pip tk"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_info "Python Version: $PYTHON_VERSION"

# Python Version Check (mindestens 3.8)
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8 oder höher wird benötigt (gefunden: $PYTHON_VERSION)"
    exit 1
fi

# 2. Tkinter prüfen
print_info "Prüfe Tkinter Installation..."
if ! python3 -c "import tkinter" 2>/dev/null; then
    print_error "Tkinter ist nicht installiert!"
    echo "Bitte installiere Tkinter:"
    echo "  Ubuntu/Debian: sudo apt install python3-tk"
    echo "  Fedora/RHEL:   sudo dnf install python3-tkinter"
    echo "  Arch:          sudo pacman -S tk"
    exit 1
fi
print_info "Tkinter ist installiert"

# 3. pip prüfen
print_info "Prüfe pip Installation..."
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    print_error "pip ist nicht installiert!"
    echo "Bitte installiere pip:"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    echo "  Fedora/RHEL:   sudo dnf install python3-pip"
    exit 1
fi
print_info "pip ist installiert"

# 4. Virtual Environment Support prüfen
print_info "Prüfe venv Modul..."
if ! python3 -c "import venv" 2>/dev/null; then
    print_error "venv Modul ist nicht verfügbar!"
    echo "Bitte installiere python3-venv:"
    echo "  Ubuntu/Debian: sudo apt install python3-venv"
    exit 1
fi
print_info "venv Modul ist verfügbar"

# 5. Git prüfen (optional, falls Repo geklont werden soll)
if ! command -v git &> /dev/null; then
    print_warning "Git ist nicht installiert. Manuelle Installation erforderlich."
else
    print_info "Git ist installiert"
fi

echo ""
print_info "Alle Voraussetzungen erfüllt!"
echo ""

# 6. Virtual Environment erstellen
if [ -d ".venv" ]; then
    print_warning "Virtual Environment existiert bereits"
    read -p "Möchten Sie es neu erstellen? (j/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        print_info "Lösche altes Virtual Environment..."
        rm -rf .venv
        print_info "Erstelle neues Virtual Environment..."
        python3 -m venv .venv
    fi
else
    print_info "Erstelle Virtual Environment..."
    python3 -m venv .venv
fi

# 7. Virtual Environment aktivieren
print_info "Aktiviere Virtual Environment..."
source .venv/bin/activate

# 8. pip aktualisieren
print_info "Aktualisiere pip..."
python3 -m pip install --upgrade pip

# 9. Dependencies installieren
print_info "Installiere Abhängigkeiten..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_info "Alle Abhängigkeiten wurden installiert"
else
    print_error "requirements.txt nicht gefunden!"
    exit 1
fi

# 10. Überprüfe Installation
print_info "Überprüfe Installation..."
if python3 -c "import matplotlib" 2>/dev/null; then
    print_info "matplotlib erfolgreich installiert"
else
    print_error "matplotlib konnte nicht importiert werden"
    exit 1
fi

# 11. Konfiguration
echo ""
print_info "Installation abgeschlossen!"
echo ""

if [ ! -f "config.ini" ]; then
    print_warning "config.ini wurde nicht gefunden"
    print_info "Eine Beispiel-Konfiguration wird beim ersten Start erstellt"
    print_info "Standard-Datenbank-Pfad: ~/.local/share/hamradio/QLog/qlog.db"
else
    print_info "config.ini gefunden"
fi

# 12. run.sh ausführbar machen
if [ -f "run.sh" ]; then
    chmod +x run.sh
    print_info "run.sh wurde ausführbar gemacht"
fi

# Abschluss
echo ""
echo "=========================================="
echo "  Installation erfolgreich!"
echo "=========================================="
echo ""
echo "Um Qlog-Stats zu starten, verwenden Sie:"
echo "  ./run.sh"
echo ""
echo "Oder manuell:"
echo "  source .venv/bin/activate"
echo "  python3 main.py"
echo ""
echo "Beim ersten Start:"
echo "  1. Programm starten"
echo "  2. Datei → Datenbank-Pfad ändern"
echo "  3. Pfad zur qlog.db Datei angeben"
echo "     (Standard: ~/.local/share/hamradio/QLog/qlog.db)"
echo ""
