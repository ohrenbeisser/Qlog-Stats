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
from .context_menu import ContextMenu


class Statistics:
    """Verwaltet alle Statistik-Anzeigen mit einheitlicher Logik"""

    def __init__(self, db, table_view, plot_view, date_filter, paned_window, export_handler, config_manager, parent_window):
        """
        Initialisiert den Statistics Handler

        Args:
            db: QlogDatabase Instanz
            table_view: TableView Instanz
            plot_view: PlotView Instanz
            date_filter: DateFilter Instanz
            paned_window: PanedWindow Widget
            export_handler: ExportHandler Instanz
            config_manager: ConfigManager Instanz für Spalten-Konfiguration
            parent_window: Parent-Fenster für Dialoge
        """
        self.db = db
        self.table_view = table_view
        self.plot_view = plot_view
        self.date_filter = date_filter
        self.paned_window = paned_window
        self.export_handler = export_handler
        self.config_manager = config_manager
        self.parent_window = parent_window
        self.current_type = None
        self.context_menu = None

        # Lade konfigurierte Detail-Spalten
        self._detail_columns = self.config_manager.get_detail_columns()

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
                'columns': None,  # Wird dynamisch geladen
                'table_label': 'Sonderrufzeichen',
                'plot_title': None,
                'plot_xlabel': None,
                'plot_ylabel': None,
                'show_plot': False,
                'on_double_click': 'qrz'
            },
            'weekday': {
                'db_method': 'get_qsos_by_weekday',
                'db_params': {},
                'columns': ['weekday', 'count'],
                'table_label': 'Tabelle',
                'plot_title': 'QSOs nach Wochentagen',
                'plot_xlabel': 'Wochentag',
                'plot_ylabel': 'Anzahl QSOs',
                'show_plot': True,
                'on_double_click': None
            },
            'month': {
                'db_method': 'get_qsos_by_month',
                'db_params': {},
                'columns': ['month', 'count'],
                'table_label': 'Tabelle',
                'plot_title': 'QSOs nach Monaten',
                'plot_xlabel': 'Monat',
                'plot_ylabel': 'Anzahl QSOs',
                'show_plot': True,
                'on_double_click': None
            },
            'day': {
                'db_method': 'get_qsos_by_day',
                'db_params': {},
                'columns': ['day', 'count'],
                'table_label': 'Tabelle',
                'plot_title': 'QSOs nach Tagen',
                'plot_xlabel': 'Tag des Monats',
                'plot_ylabel': 'Anzahl QSOs',
                'show_plot': True,
                'on_double_click': None,
                'plot_limit': 31
            },
            'hour': {
                'db_method': 'get_qsos_by_hour',
                'db_params': {},
                'columns': ['hour', 'count'],
                'table_label': 'Tabelle',
                'plot_title': 'QSOs nach Stunden',
                'plot_xlabel': 'Stunde',
                'plot_ylabel': 'Anzahl QSOs',
                'show_plot': True,
                'on_double_click': None,
                'plot_limit': 24
            },
            'callsign': {
                'db_method': 'get_qsos_by_callsign',
                'db_params': {'limit': 1000},
                'columns': ['callsign', 'count'],
                'table_label': 'Tabelle',
                'plot_title': 'QSOs nach Rufzeichen (Top 20)',
                'plot_xlabel': 'Rufzeichen',
                'plot_ylabel': 'Anzahl QSOs',
                'show_plot': True,
                'on_double_click': 'qrz'
            },
            'top_days': {
                'db_method': 'get_top_qso_days',
                'db_params': {'limit': 250},
                'columns': ['date', 'count'],
                'table_label': 'Tabelle',
                'plot_title': 'Top QSO-Tage (Top 250)',
                'plot_xlabel': 'Datum',
                'plot_ylabel': 'Anzahl QSOs',
                'show_plot': True,
                'on_double_click': None
            },
            'flop_days': {
                'db_method': 'get_flop_qso_days',
                'db_params': {'limit': 250},
                'columns': ['date', 'count'],
                'table_label': 'Tabelle',
                'plot_title': 'Flop QSO-Tage (250 Tage)',
                'plot_xlabel': 'Datum',
                'plot_ylabel': 'Anzahl QSOs',
                'show_plot': True,
                'on_double_click': None
            },
            'callsign_search': {
                'db_method': 'search_callsigns',
                'db_params': {},  # wird dynamisch gefüllt
                'columns': None,  # Wird dynamisch geladen
                'table_label': 'Suchergebnisse',
                'plot_title': None,
                'plot_xlabel': None,
                'plot_ylabel': None,
                'show_plot': False,
                'on_double_click': 'qrz'
            },
            'qsl_sent': {
                'db_method': 'get_qsl_sent',
                'db_params': {},
                'columns': None,  # Wird dynamisch geladen (mit qsl_date)
                'table_label': 'Versendete QSL-Karten',
                'plot_title': None,
                'plot_xlabel': None,
                'plot_ylabel': None,
                'show_plot': False,
                'on_double_click': 'qrz'
            },
            'qsl_received': {
                'db_method': 'get_qsl_received',
                'db_params': {},
                'columns': None,  # Wird dynamisch geladen (mit qsl_date)
                'table_label': 'Erhaltene QSL-Karten',
                'plot_title': None,
                'plot_xlabel': None,
                'plot_ylabel': None,
                'show_plot': False,
                'on_double_click': 'qrz'
            },
            'qsl_requested': {
                'db_method': 'get_qsl_requested',
                'db_params': {},
                'columns': None,  # Wird dynamisch geladen
                'table_label': 'Angeforderte QSL-Karten',
                'plot_title': None,
                'plot_xlabel': None,
                'plot_ylabel': None,
                'show_plot': False,
                'on_double_click': 'qrz'
            },
            'qsl_queued': {
                'db_method': 'get_qsl_queued',
                'db_params': {},
                'columns': None,  # Wird dynamisch geladen
                'table_label': 'Zu versendende QSL-Karten',
                'plot_title': None,
                'plot_xlabel': None,
                'plot_ylabel': None,
                'show_plot': False,
                'on_double_click': 'qrz'
            },
            'lotw_received': {
                'db_method': 'get_lotw_received',
                'db_params': {},
                'columns': None,  # Wird dynamisch geladen (mit qsl_date)
                'table_label': 'LotW-Bestätigungen',
                'plot_title': None,
                'plot_xlabel': None,
                'plot_ylabel': None,
                'show_plot': False,
                'on_double_click': 'qrz'
            },
            'eqsl_received': {
                'db_method': 'get_eqsl_received',
                'db_params': {},
                'columns': None,  # Wird dynamisch geladen (mit qsl_date)
                'table_label': 'eQSL-Bestätigungen',
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
            filters = self.date_filter.get_filters()

            # 2. Suchzeile ein-/ausblenden je nach Statistik-Typ
            qsl_types = ['qsl_sent', 'qsl_received', 'qsl_requested', 'qsl_queued',
                        'lotw_received', 'eqsl_received']
            if stat_type not in ['callsign_search', 'special'] + qsl_types:
                # Bei Statistiken außer Suche, Sonderrufzeichen und QSL: Suchzeile ausblenden
                self.date_filter.hide_search_row()

            # 3. Tabellen-Label setzen (z.B. "Tabelle" oder "Sonderrufzeichen")
            self.table_view.set_label(config['table_label'])

            # 3. Filter intelligent anpassen je nach Statistik-Typ
            # Entferne den entsprechenden Filter bei gruppierter Anzeige
            filter_params = filters.copy()
            if stat_type == 'country':
                # Bei Länder-Statistik: Kein Land-Filter
                filter_params.pop('country', None)
            elif stat_type == 'band':
                # Bei Band-Statistik: Kein Band-Filter
                filter_params.pop('band', None)
            elif stat_type == 'mode':
                # Bei Mode-Statistik: Kein Mode-Filter
                filter_params.pop('mode', None)

            # 4. Spalten für Detail-Tabellen dynamisch bestimmen
            # QSL-Tabellen mit qsl_date
            qsl_with_date = ['qsl_sent', 'qsl_received', 'lotw_received', 'eqsl_received']
            # QSL-Tabellen ohne qsl_date
            qsl_without_date = ['qsl_requested', 'qsl_queued']
            # Alle Detail-Tabellen
            detail_tables = ['special', 'callsign_search'] + qsl_with_date + qsl_without_date

            display_columns = config['columns']
            if display_columns is None and stat_type in detail_tables:
                # Dynamisch aus Config laden
                display_columns = self._detail_columns.copy()

                # Füge qsl_date hinzu für QSL-Tabellen mit Datum
                if stat_type in qsl_with_date and 'qsl_date' not in display_columns:
                    display_columns.append('qsl_date')

            # 5. Daten aus Datenbank abrufen
            db_method = getattr(self.db, config['db_method'])
            params = {**config['db_params'], **filter_params}

            # Füge columns-Parameter für Detail-Tabellen hinzu
            if stat_type in detail_tables:
                params['columns'] = display_columns

            # Spezialbehandlung für Rufzeichen-Suche
            if stat_type == 'callsign_search':
                search_params = self.date_filter.get_search_params()
                if search_params:
                    # Mit Suchbegriff: Normale Suche durchführen
                    params['search_term'] = search_params['search_term']
                    params['search_mode'] = search_params['search_mode']
                else:
                    # Ohne Suchbegriff: Alle QSOs anzeigen (mit Filter)
                    # Verwende einen leeren Suchbegriff mit Teilstring-Modus (zeigt alle)
                    params['search_term'] = ''
                    params['search_mode'] = 'partial'

            data = db_method(**params)

            # Spezialbehandlung für Sonderrufzeichen-Filter
            if stat_type == 'special':
                search_params = self.date_filter.get_search_params()
                if search_params and search_params['search_term']:
                    # Filtere Sonderrufzeichen nach Suchbegriff
                    search_term = search_params['search_term'].upper()
                    search_mode = search_params['search_mode']

                    filtered_data = []
                    for row in data:
                        callsign = row.get('callsign', '').upper()

                        if search_mode == 'beginning':
                            # Suche vom Beginn des Rufzeichens
                            if callsign.startswith(search_term):
                                filtered_data.append(row)
                        else:  # partial
                            # Teilstring-Suche
                            if search_term in callsign:
                                filtered_data.append(row)

                    data = filtered_data

            # 6. Event-Handler konfigurieren (z.B. Doppelklick für QRZ-Links)
            on_double_click = None
            if config['on_double_click'] == 'qrz':
                on_double_click = QRZIntegration.create_callback(self.table_view.get_tree())

            # 7. Tabelle mit Daten füllen
            # Verwende display_columns für Detail-Tabellen, sonst config['columns']
            table_columns = display_columns if display_columns else config['columns']
            self.table_view.populate(table_columns, data, on_double_click=on_double_click)

            # 7b. Aktiviere Kontextmenü für Detail-Tabellen
            if stat_type in detail_tables:
                # Erstelle oder aktualisiere Kontextmenü
                if not self.context_menu:
                    self.context_menu = ContextMenu(
                        self.table_view.get_tree(),
                        self.db,
                        self.parent_window
                    )
            else:
                # Deaktiviere Kontextmenü für Statistik-Tabellen
                self.context_menu = None

            # 8. Diagramm-Anzeige steuern
            if config['show_plot']:
                # Diagramm anzeigen (falls versteckt, wieder einblenden)
                if self.plot_view.parent_frame not in self.paned_window.panes():
                    self.paned_window.add(self.plot_view.parent_frame, minsize=300)

                # Diagramm mit Daten aktualisieren
                plot_limit = config.get('plot_limit', 20)  # Standard: 20 Datenpunkte
                self.plot_view.update_plot(
                    data,
                    config['columns'][0],  # X-Achse (z.B. 'country')
                    config['columns'][1],  # Y-Achse (z.B. 'count')
                    config['plot_title'],
                    config['plot_xlabel'],
                    config['plot_ylabel'],
                    limit=plot_limit
                )
            else:
                # Diagramm verstecken (z.B. bei Sonderrufzeichen)
                try:
                    self.paned_window.forget(self.plot_view.parent_frame)
                except:
                    pass  # Panel war bereits entfernt

            # 9. Aktuellen Zustand speichern für Export und Refresh
            self.current_type = stat_type
            self.export_handler.set_current_data(data, stat_type)

            # 10. QSO-Zähler aktualisieren
            self.date_filter.update_info()

            # 11. Bei Rufzeichen-Suche und QSL-Ansichten: Ergebnis-Anzahl aktualisieren
            qsl_types = ['qsl_sent', 'qsl_received', 'qsl_requested', 'qsl_queued',
                        'lotw_received', 'eqsl_received']
            if stat_type in ['callsign_search'] + qsl_types:
                self.date_filter.update_search_result_count(len(data))

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

    def reload_columns(self):
        """Lädt die konfigurierten Spalten neu (nach Änderung in Einstellungen)"""
        self._detail_columns = self.config_manager.get_detail_columns()
        # Aktualisiere die aktuelle Ansicht, falls eine Detail-Tabelle angezeigt wird
        if self.current_type:
            self.refresh_current()
