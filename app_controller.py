"""
Application Controller für Qlog-Stats
======================================

Hauptanwendungs-Controller, der alle UI- und Feature-Module orchestriert.

Architektur:
-----------
    UI-Layer:
        - MainWindow: Fenster-Layout und Menü
        - TableView: Sortierbare Tabellen-Anzeige
        - PlotView: Matplotlib-Diagramme

    Feature-Layer:
        - Statistics: Vereinheitlichte Statistik-Anzeige
        - DateFilter: Datumsfilter-Verwaltung
        - ExportHandler: CSV/TXT Export-Koordination
        - QRZIntegration: QRZ.com Link-Integration

    Data-Layer:
        - QlogDatabase: Nur-Lese Zugriff auf Qlog SQLite DB
        - StatsExporter: Export-Funktionalität
        - ConfigManager: INI-Konfigurationsverwaltung

Verwendung:
----------
    root = tk.Tk()
    app = QlogStatsApp(root)
    app.run()

Autor: Claude AI
Lizenz: MIT
"""

import os
from tkinter import messagebox, filedialog

from config_manager import ConfigManager
from database import QlogDatabase
from stats_exporter import StatsExporter

from ui import MainWindow, TableView, PlotView
from features import Statistics, DateFilter, ExportHandler, QRZIntegration


class QlogStatsApp:
    """Hauptanwendung - orchestriert alle Module"""

    def __init__(self, root):
        """
        Initialisiert die Anwendung

        Args:
            root: Tkinter Root-Fenster
        """
        self.root = root
        self.root.title("Qlog-Stats - QSO Statistik Auswertung")

        self.config = ConfigManager()
        self.db = None
        self.exporter = None

        # UI-Komponenten
        self.main_window = None
        self.table_view = None
        self.plot_view = None

        # Feature-Komponenten
        self.statistics = None
        self.date_filter = None
        self.export_handler = None

        width, height = self.config.get_window_size()
        self.root.geometry(f"{width}x{height}")

        self._setup_ui()
        self._init_database()

    def _setup_ui(self):
        """Erstellt die Benutzeroberfläche durch Orchestrierung der Module"""
        # Callbacks für das Hauptfenster
        # WICHTIG: Verwende Methoden statt Lambdas, da self.statistics/export_handler
        # zum Zeitpunkt der Callback-Erstellung noch None sind
        callbacks = {
            'change_db_path': self._change_db_path,
            'quit': self.root.quit,
            'show_country': self._show_country,
            'show_band': self._show_band,
            'show_mode': self._show_mode,
            'show_year': self._show_year,
            'show_special': self._show_special,
            'export_csv': self._export_csv,
            'export_txt': self._export_txt
        }

        # Hauptfenster erstellen
        self.main_window = MainWindow(self.root, callbacks)

        # Tabellen-View erstellen
        self.table_view = TableView(self.main_window.get_table_frame())

        # Plot-View erstellen
        self.plot_view = PlotView(self.main_window.get_plot_frame())

        # Export-Handler erstellen (exporter wird in _init_database() gesetzt)
        self.export_handler = ExportHandler(None)

        # Date-Filter erstellen (db wird in _init_database() gesetzt)
        self.date_filter = DateFilter(
            self.main_window.get_filter_frame(),
            self.db,
            self._on_filter_change
        )

        # Statistics erstellen (db wird in _init_database() gesetzt)
        self.statistics = Statistics(
            self.db,
            self.table_view,
            self.plot_view,
            self.date_filter,
            self.main_window.get_paned_window(),
            self.export_handler
        )

    def _init_database(self):
        """Initialisiert die Datenbankverbindung"""
        db_path = self.config.get_db_path()

        if not os.path.exists(db_path):
            messagebox.showerror("Fehler",
                               f"Datenbank nicht gefunden:\n{db_path}\n\n"
                               "Bitte Pfad unter 'Datei -> Datenbank-Pfad ändern' anpassen.")
            return

        try:
            self.db = QlogDatabase(db_path)
            self.exporter = StatsExporter(self.config.get_export_directory())

            # DB und Exporter den Modulen zuweisen
            self.date_filter.db = self.db
            self.statistics.db = self.db
            self.export_handler.exporter = self.exporter

            # Datumsbereich laden (rufe öffentliche Methode auf, nicht private)
            date_range = self.db.get_date_range()
            self.date_filter.start_date_var.set(date_range['min_date'])
            self.date_filter.end_date_var.set(date_range['max_date'])
            self.date_filter.update_info()

            # Erste Statistik anzeigen
            self.root.after(200, lambda: self.statistics.show_statistics('country'))

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Datenbank:\n{str(e)}")

    def _change_db_path(self):
        """Dialog zum Ändern des Datenbank-Pfads"""
        new_path = filedialog.askopenfilename(
            title="Qlog-Datenbank auswählen",
            filetypes=[("SQLite Datenbank", "*.db"), ("Alle Dateien", "*.*")]
        )

        if new_path:
            self.config.set_db_path(new_path)
            if self.db:
                self.db.disconnect()
            self._init_database()

    def _on_filter_change(self):
        """Callback wenn sich der Datumsfilter ändert"""
        if self.statistics:
            self.statistics.refresh_current()

    # Callback-Methoden für Menü-Aktionen
    # Diese delegieren an die entsprechenden Module

    def _show_country(self):
        """Zeigt Länder-Statistik an"""
        if self.statistics:
            self.statistics.show_statistics('country')

    def _show_band(self):
        """Zeigt Band-Statistik an"""
        if self.statistics:
            self.statistics.show_statistics('band')

    def _show_mode(self):
        """Zeigt Mode-Statistik an"""
        if self.statistics:
            self.statistics.show_statistics('mode')

    def _show_year(self):
        """Zeigt Jahr-Statistik an"""
        if self.statistics:
            self.statistics.show_statistics('year')

    def _show_special(self):
        """Zeigt Sonderrufzeichen an"""
        if self.statistics:
            self.statistics.show_statistics('special')

    def _export_csv(self):
        """Exportiert aktuelle Daten als CSV"""
        if self.export_handler:
            self.export_handler.export_csv()

    def _export_txt(self):
        """Exportiert aktuelle Daten als TXT"""
        if self.export_handler:
            self.export_handler.export_txt()

    def run(self):
        """Startet die Anwendung"""
        self.root.mainloop()
