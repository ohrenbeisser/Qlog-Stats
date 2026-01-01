"""
Statistics Module für Qlog-Stats
=================================

Verwaltet die Statistik-Anzeige mit vereinheitlichter Logik.

Dieses Modul ersetzt die ursprünglich 5 fast identischen Methoden
(_show_country_stats, _show_band_stats, _show_mode_stats, _show_year_stats,
_show_special_callsigns) durch eine einzige konfigurierbare Methode.

Design Pattern: Strategy Pattern
--------------------------------
Jeder Statistik-Typ (country, band, mode, year, special) wird durch eine
Konfiguration beschrieben, die folgende Aspekte definiert:
    - DB-Abfrage-Methode
    - Spalten für Tabelle
    - Plot-Konfiguration (Titel, Labels)
    - Spezielle Event-Handler (z.B. QRZ-Links)

Vorteile:
---------
    - Code-Reduktion: ~100 Zeilen weniger
    - Einheitliches Verhalten aller Statistik-Typen
    - Einfache Erweiterbarkeit: Neue Statistik-Typen durch Config hinzufügen
    - Zentrale Fehlerbehandlung

Verwendung:
----------
    stats = Statistics(db, table_view, plot_view, date_filter, paned_window, export_handler)
    stats.show_statistics('country')  # Zeigt Länder-Statistik
    stats.show_statistics('special')  # Zeigt Sonderrufzeichen
"""

from tkinter import messagebox
from .qrz_integration import QRZIntegration


class Statistics:
    """Verwaltet alle Statistik-Anzeigen mit einheitlicher Logik"""

    def __init__(self, db, table_view, plot_view, date_filter, paned_window, export_handler):
        """
        Initialisiert den Statistics Handler

        Args:
            db: QlogDatabase Instanz
            table_view: TableView Instanz
            plot_view: PlotView Instanz
            date_filter: DateFilter Instanz
            paned_window: PanedWindow Widget
            export_handler: ExportHandler Instanz
        """
        self.db = db
        self.table_view = table_view
        self.plot_view = plot_view
        self.date_filter = date_filter
        self.paned_window = paned_window
        self.export_handler = export_handler
        self.current_type = None

        # Konfiguration für jeden Statistik-Typ
        self.stat_configs = {
            'country': {
                'db_method': 'get_qsos_by_country',
                'db_params': {},
                'columns': ['country', 'count'],
                'table_label': 'Tabelle',
                'plot_title': 'QSOs nach Ländern (Top 20)',
                'plot_xlabel': 'Land',
                'plot_ylabel': 'Anzahl QSOs',
                'show_plot': True,
                'on_double_click': None
            },
            'band': {
                'db_method': 'get_qsos_by_band',
                'db_params': {},
                'columns': ['band', 'count'],
                'table_label': 'Tabelle',
                'plot_title': 'QSOs nach Bändern',
                'plot_xlabel': 'Band',
                'plot_ylabel': 'Anzahl QSOs',
                'show_plot': True,
                'on_double_click': None
            },
            'mode': {
                'db_method': 'get_qsos_by_mode',
                'db_params': {},
                'columns': ['mode', 'count'],
                'table_label': 'Tabelle',
                'plot_title': 'QSOs nach Modes',
                'plot_xlabel': 'Mode',
                'plot_ylabel': 'Anzahl QSOs',
                'show_plot': True,
                'on_double_click': None
            },
            'year': {
                'db_method': 'get_qsos_by_year',
                'db_params': {},
                'columns': ['year', 'count'],
                'table_label': 'Tabelle',
                'plot_title': 'QSOs nach Jahren',
                'plot_xlabel': 'Jahr',
                'plot_ylabel': 'Anzahl QSOs',
                'show_plot': True,
                'on_double_click': None
            },
            'special': {
                'db_method': 'get_special_callsigns',
                'db_params': {},
                'columns': ['callsign', 'date', 'time', 'band', 'mode', 'country', 'qrz'],
                'table_label': 'Sonderrufzeichen',
                'plot_title': None,
                'plot_xlabel': None,
                'plot_ylabel': None,
                'show_plot': False,
                'on_double_click': 'qrz'
            }
        }

    def show_statistics(self, stat_type):
        """
        Zeigt Statistik für gegebenen Typ (Zentrale Methode für alle Statistiken)

        Diese Methode implementiert den gesamten Ablauf für die Anzeige von Statistiken:
        1. Konfiguration laden
        2. Daten aus DB abrufen
        3. Tabelle aktualisieren
        4. Diagramm zeigen/verstecken
        5. Daten für Export bereitstellen

        Args:
            stat_type: Typ der Statistik (country, band, mode, year, special)

        Raises:
            Zeigt Fehlerdialog bei Problemen
        """
        # Validierung
        if not self.db:
            return

        if stat_type not in self.stat_configs:
            messagebox.showerror("Fehler", f"Unbekannter Statistik-Typ: {stat_type}")
            return

        try:
            # 1. Konfiguration und Parameter abrufen
            config = self.stat_configs[stat_type]
            start_date, end_date = self.date_filter.get_dates()

            # 2. Tabellen-Label setzen (z.B. "Tabelle" oder "Sonderrufzeichen")
            self.table_view.set_label(config['table_label'])

            # 3. Daten aus Datenbank abrufen
            db_method = getattr(self.db, config['db_method'])
            params = {**config['db_params'], 'start_date': start_date, 'end_date': end_date}
            data = db_method(**params)

            # 4. Spezielle Datenaufbereitung für Sonderrufzeichen
            # Füge 'Link' Text in QRZ-Spalte ein
            if stat_type == 'special':
                for row in data:
                    row['qrz'] = 'Link'

            # 5. Event-Handler konfigurieren (z.B. Doppelklick für QRZ-Links)
            on_double_click = None
            if config['on_double_click'] == 'qrz':
                on_double_click = QRZIntegration.create_callback(self.table_view.get_tree())

            # 6. Tabelle mit Daten füllen
            self.table_view.populate(config['columns'], data, on_double_click=on_double_click)

            # 7. Diagramm-Anzeige steuern
            if config['show_plot']:
                # Diagramm anzeigen (falls versteckt, wieder einblenden)
                if self.plot_view.parent_frame not in self.paned_window.panes():
                    self.paned_window.add(self.plot_view.parent_frame, minsize=300)

                # Diagramm mit Daten aktualisieren
                self.plot_view.update_plot(
                    data,
                    config['columns'][0],  # X-Achse (z.B. 'country')
                    config['columns'][1],  # Y-Achse (z.B. 'count')
                    config['plot_title'],
                    config['plot_xlabel'],
                    config['plot_ylabel'],
                    limit=20  # Maximal 20 Datenpunkte im Diagramm
                )
            else:
                # Diagramm verstecken (z.B. bei Sonderrufzeichen)
                if self.plot_view.parent_frame in self.paned_window.panes():
                    self.paned_window.forget(self.plot_view.parent_frame)

            # 8. Aktuellen Zustand speichern für Export und Refresh
            self.current_type = stat_type
            self.export_handler.set_current_data(data, stat_type)

            # 9. QSO-Zähler aktualisieren
            self.date_filter.update_info()

        except Exception as e:
            # Zentrales Error-Handling: Zeige Fehlermeldung
            messagebox.showerror("Fehler", f"Fehler beim Laden der Statistik:\n{str(e)}")

    def get_current_type(self):
        """Gibt den aktuellen Statistik-Typ zurück"""
        return self.current_type

    def refresh_current(self):
        """Aktualisiert die aktuelle Statistik-Anzeige"""
        if self.current_type:
            self.show_statistics(self.current_type)
