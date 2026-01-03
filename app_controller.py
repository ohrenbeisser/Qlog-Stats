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
from features.query_builder import QueryBuilderDialog
from query_manager import QueryManager


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
        self.query_manager = QueryManager()  # Query Manager für benutzerdefinierte Abfragen

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
            'show_month': self._show_month,
            'show_weekday': self._show_weekday,
            'show_day': self._show_day,
            'show_hour': self._show_hour,
            'show_callsign': self._show_callsign,
            'show_top_days': self._show_top_days,
            'show_flop_days': self._show_flop_days,
            'show_search': self._show_search,
            'show_special': self._show_special,
            'show_qsl_sent': self._show_qsl_sent,
            'show_qsl_received': self._show_qsl_received,
            'show_qsl_requested': self._show_qsl_requested,
            'show_qsl_queued': self._show_qsl_queued,
            'show_lotw_received': self._show_lotw_received,
            'show_eqsl_received': self._show_eqsl_received,
            'export_csv': self._export_csv,
            'export_txt': self._export_txt,
            'show_about': self._show_about,
            'new_query': self._new_query,
            'run_query': self._run_query,
            'manage_queries': self._manage_queries
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
            self.main_window.get_search_frame(),
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

        # Such-Callback verbinden
        self.date_filter.search_callback = self._perform_callsign_search

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

            # Filter-Optionen laden (Band, Mode, Land)
            self.date_filter._load_filter_options()

            self.date_filter.update_info()

            # Erste Statistik anzeigen
            self.root.after(200, lambda: self.statistics.show_statistics('country'))

            # Lade gespeicherte Abfragen ins Menü
            self._update_queries_menu()

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

    def _perform_callsign_search(self):
        """Führt die Rufzeichen-Suche aus"""
        if self.statistics:
            self.statistics.show_statistics('callsign_search')

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

    def _show_search(self):
        """Zeigt Rufzeichen-Suche an"""
        if self.date_filter and self.statistics:
            # Suchzeile einblenden und Fokus setzen
            self.date_filter.show_search_row()
            # Sofort alle QSOs anzeigen (mit aktuellen Filtern)
            self.statistics.show_statistics('callsign_search')

    def _show_special(self):
        """Zeigt Sonderrufzeichen an"""
        if self.date_filter and self.statistics:
            self.date_filter.show_search_row()
            self.statistics.show_statistics('special')

    def _show_qsl_sent(self):
        """Zeigt versendete QSL-Karten an"""
        if self.date_filter and self.statistics:
            self.date_filter.show_search_row()
            self.statistics.show_statistics('qsl_sent')

    def _show_qsl_received(self):
        """Zeigt erhaltene QSL-Karten an"""
        if self.date_filter and self.statistics:
            self.date_filter.show_search_row()
            self.statistics.show_statistics('qsl_received')

    def _show_qsl_requested(self):
        """Zeigt angeforderte QSL-Karten an"""
        if self.date_filter and self.statistics:
            self.date_filter.show_search_row()
            self.statistics.show_statistics('qsl_requested')

    def _show_qsl_queued(self):
        """Zeigt zu versendende QSL-Karten an"""
        if self.date_filter and self.statistics:
            self.date_filter.show_search_row()
            self.statistics.show_statistics('qsl_queued')

    def _show_lotw_received(self):
        """Zeigt LotW-Bestätigungen an"""
        if self.date_filter and self.statistics:
            self.date_filter.show_search_row()
            self.statistics.show_statistics('lotw_received')

    def _show_eqsl_received(self):
        """Zeigt eQSL-Bestätigungen an"""
        if self.date_filter and self.statistics:
            self.date_filter.show_search_row()
            self.statistics.show_statistics('eqsl_received')

    def _show_weekday(self):
        """Zeigt Wochentag-Statistik an"""
        if self.statistics:
            self.statistics.show_statistics('weekday')

    def _show_month(self):
        """Zeigt Monats-Statistik an"""
        if self.statistics:
            self.statistics.show_statistics('month')

    def _show_day(self):
        """Zeigt Tag-Statistik an"""
        if self.statistics:
            self.statistics.show_statistics('day')

    def _show_hour(self):
        """Zeigt Stunden-Statistik an"""
        if self.statistics:
            self.statistics.show_statistics('hour')

    def _show_callsign(self):
        """Zeigt Rufzeichen-Statistik an"""
        if self.statistics:
            self.statistics.show_statistics('callsign')

    def _show_top_days(self):
        """Zeigt Top QSO-Tage an"""
        if self.statistics:
            self.statistics.show_statistics('top_days')

    def _show_flop_days(self):
        """Zeigt Flop QSO-Tage an"""
        if self.statistics:
            self.statistics.show_statistics('flop_days')

    def _export_csv(self):
        """Exportiert aktuelle Daten als CSV"""
        if self.export_handler:
            self.export_handler.export_csv()

    def _export_txt(self):
        """Exportiert aktuelle Daten als TXT"""
        if self.export_handler:
            self.export_handler.export_txt()

    def _show_about(self):
        """Zeigt den Über-Dialog an"""
        import tkinter as tk
        from tkinter import ttk

        about_window = tk.Toplevel(self.root)
        about_window.title("Über Qlog-Stats")
        about_window.geometry("500x350")
        about_window.resizable(False, False)

        # Zentriere das Fenster
        about_window.transient(self.root)
        about_window.grab_set()

        # Haupt-Frame mit Padding
        main_frame = ttk.Frame(about_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Titel
        title_label = ttk.Label(main_frame, text="Qlog-Stats",
                               font=('TkDefaultFont', 24, 'bold'))
        title_label.pack(pady=(0, 20))

        # Info-Frame
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Info-Einträge
        info_data = [
            ("Version:", "0.0.1"),
            ("Autor:", "Chris (DL6LG)"),
            ("Lizenz:", "MIT"),
            ("GitHub:", "https://github.com/DL6LG/Qlog-Stats")
        ]

        for i, (label_text, value_text) in enumerate(info_data):
            label = ttk.Label(info_frame, text=label_text,
                            font=('TkDefaultFont', 10, 'bold'))
            label.grid(row=i, column=0, sticky='w', padx=(0, 10), pady=5)

            value = ttk.Label(info_frame, text=value_text,
                            font=('TkDefaultFont', 10))
            value.grid(row=i, column=1, sticky='w', pady=5)

        # Beschreibung
        desc_text = "Statistik-Auswertung für Qlog - Amateur Radio Logging"
        desc_label = ttk.Label(main_frame, text=desc_text,
                              font=('TkDefaultFont', 9),
                              wraplength=450, justify='center')
        desc_label.pack(pady=(20, 20))

        # OK-Button
        ok_button = ttk.Button(main_frame, text="OK",
                              command=about_window.destroy,
                              width=10)
        ok_button.pack(pady=(10, 0))

        # Zentriere das Fenster auf dem Hauptfenster
        about_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (about_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (about_window.winfo_height() // 2)
        about_window.geometry(f"+{x}+{y}")

    def _new_query(self):
        """Öffnet den Dialog für eine neue Abfrage"""
        dialog = QueryBuilderDialog(self.root, self.query_manager)
        result = dialog.show()

        if result:
            # Aktualisiere Menü mit neuer Abfrage
            self._update_queries_menu()

    def _run_query(self, query_id):
        """Führt eine gespeicherte Abfrage aus"""
        query = self.query_manager.get_query(query_id)

        if not query:
            messagebox.showerror("Fehler", "Abfrage nicht gefunden.")
            return

        try:
            # Bestimme SQL basierend auf Abfrage-Typ
            query_type = query.get('type', 'builder')

            if query_type == 'sql':
                # Direkte SQL-Abfrage
                sql = query.get('sql', '')
                # Bei SQL-Abfragen: Extrahiere Spaltennamen aus SQL
                # Einfache Heuristik: SELECT col1, col2, ... FROM
                import re
                match = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE)
                if match:
                    cols_str = match.group(1)
                    if cols_str.strip() == '*':
                        display_columns = []  # Alle Spalten
                    else:
                        # Extrahiere Spaltennamen (berücksichtige "as alias")
                        col_parts = [c.strip() for c in cols_str.split(',')]
                        display_columns = []
                        for part in col_parts:
                            if ' as ' in part.lower():
                                # "column as alias" -> nehme alias
                                alias = part.split(' as ')[-1].strip()
                                display_columns.append(alias)
                            else:
                                display_columns.append(part)
                else:
                    display_columns = []
            else:
                # Builder-Abfrage
                from features.query_builder import QueryBuilderDialog
                sql = QueryBuilderDialog._generate_sql(None, query)

                # Bestimme Spalten
                builder = query.get('builder', {})
                columns = builder.get('columns', [])

                # Wenn start_time in Spalten, ersetze durch date und time
                if 'start_time' in columns:
                    display_columns = []
                    for col in columns:
                        if col == 'start_time':
                            display_columns.extend(['date', 'time'])
                        else:
                            display_columns.append(col)
                else:
                    display_columns = columns

            # Führe Abfrage aus
            results = self.db.execute_query(sql)

            # Zeige Ergebnisse
            self.table_view.set_label(query.get('name', 'Abfrage'))

            # QRZ-Link für Doppelklick aktivieren
            from features.qrz_integration import QRZIntegration
            on_double_click = QRZIntegration.create_callback(self.table_view.get_tree())

            self.table_view.populate(display_columns, results, on_double_click=on_double_click)

            # Verstecke Plot
            try:
                self.main_window.get_paned_window().forget(self.plot_view.parent_frame)
            except:
                pass

            # Update Export-Handler
            if self.export_handler:
                self.export_handler.set_current_data(results, 'custom_query')

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Ausführen der Abfrage:\n{str(e)}")

    def _manage_queries(self):
        """Öffnet den Dialog zur Verwaltung von Abfragen"""
        from features.query_manager_dialog import QueryManagerDialog
        dialog = QueryManagerDialog(self.root, self.query_manager,
                                    on_change=self._update_queries_menu)
        dialog.show()

    def _update_queries_menu(self):
        """Aktualisiert das Abfragen-Menü mit gespeicherten Abfragen"""
        queries = self.query_manager.get_query_names()
        self.main_window.update_queries_menu(queries)

    def run(self):
        """Startet die Anwendung"""
        self.root.mainloop()
