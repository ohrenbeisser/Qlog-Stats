#!/usr/bin/env python3
"""
Qlog-Stats - Statistik-Auswertung für Qlog
Einstiegspunkt der Anwendung
"""

import tkinter as tk
from app_controller import QlogStatsApp


def main():
    """Hauptfunktion - Startet die Anwendung"""
    root = tk.Tk()
    app = QlogStatsApp(root)
    app.run()


if __name__ == '__main__':
    main()
