"""
Main Window Module für Qlog-Stats
Verwaltet das Hauptfenster, Menü und Layout
"""

import tkinter as tk
from tkinter import ttk


class MainWindow:
    """Verwaltet das Hauptfenster, Menü und Layout-Struktur"""

    def __init__(self, root, callbacks):
        """
        Initialisiert das Hauptfenster

        Args:
            root: Tkinter Root-Fenster
            callbacks: Dictionary mit Callback-Funktionen für Menü-Items:
                - 'change_db_path': Callback für Datenbank-Pfad ändern
                - 'quit': Callback für Beenden
                - 'show_country': Callback für Länder-Statistik
                - 'show_band': Callback für Band-Statistik
                - 'show_mode': Callback für Mode-Statistik
                - 'show_year': Callback für Jahr-Statistik
                - 'show_month': Callback für Monats-Statistik
                - 'show_weekday': Callback für Wochentag-Statistik
                - 'show_day': Callback für Monatstag-Statistik
                - 'show_hour': Callback für Stunden-Statistik
                - 'show_callsign': Callback für Rufzeichen-Statistik
                - 'show_top_days': Callback für Top QSO-Tage
                - 'show_flop_days': Callback für Flop QSO-Tage
                - 'show_search': Callback für Rufzeichen-Suche
                - 'show_special': Callback für Spezialcallsign
                - 'export_csv': Callback für CSV-Export
                - 'export_txt': Callback für TXT-Export
                - 'show_about': Callback für Über-Dialog
        """
        self.root = root
        self.callbacks = callbacks

        self.main_frame = None
        self.filter_frame = None
        self.paned_window = None
        self.table_frame = None
        self.plot_frame = None

        self._create_menu()
        self._create_layout()

    def _create_menu(self):
        """Erstellt die Menüleiste"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Datei", menu=file_menu)
        file_menu.add_command(label="Datenbank-Pfad ändern",
                            command=self.callbacks.get('change_db_path'))
        file_menu.add_separator()
        file_menu.add_command(label="Beenden",
                            command=self.callbacks.get('quit'))

        stats_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Statistik", menu=stats_menu)
        stats_menu.add_command(label="QSOs nach Ländern",
                             command=self.callbacks.get('show_country'))
        stats_menu.add_command(label="QSOs nach Bändern",
                             command=self.callbacks.get('show_band'))
        stats_menu.add_command(label="QSOs nach Modes",
                             command=self.callbacks.get('show_mode'))
        stats_menu.add_separator()
        stats_menu.add_command(label="QSOs nach Jahren",
                             command=self.callbacks.get('show_year'))
        stats_menu.add_command(label="QSOs nach Monaten",
                             command=self.callbacks.get('show_month'))
        stats_menu.add_command(label="QSOs nach Wochentagen",
                             command=self.callbacks.get('show_weekday'))
        stats_menu.add_command(label="QSOs nach Monatstagen",
                             command=self.callbacks.get('show_day'))
        stats_menu.add_command(label="QSOs nach Stunden",
                             command=self.callbacks.get('show_hour'))
        stats_menu.add_separator()
        stats_menu.add_command(label="Top QSO-Tage",
                             command=self.callbacks.get('show_top_days'))
        stats_menu.add_command(label="Flop QSO-Tage",
                             command=self.callbacks.get('show_flop_days'))
        stats_menu.add_separator()
        stats_menu.add_command(label="QSOs nach Rufzeichen",
                             command=self.callbacks.get('show_callsign'))

        callsign_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Rufzeichen", menu=callsign_menu)
        callsign_menu.add_command(label="Suche",
                               command=self.callbacks.get('show_search'))
        callsign_menu.add_command(label="Spezialcallsign",
                               command=self.callbacks.get('show_special'))

        export_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Export", menu=export_menu)
        export_menu.add_command(label="Als CSV exportieren",
                              command=self.callbacks.get('export_csv'))
        export_menu.add_command(label="Als TXT exportieren",
                              command=self.callbacks.get('export_txt'))

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hilfe", menu=help_menu)
        help_menu.add_command(label="Über",
                            command=self.callbacks.get('show_about'))

    def _create_layout(self):
        """Erstellt das Haupt-Layout"""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.filter_frame = ttk.LabelFrame(self.main_frame, text="Filter", padding="5")
        self.filter_frame.pack(fill=tk.X, pady=(0, 10))

        self.paned_window = tk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL,
                                          sashwidth=5, sashrelief=tk.RAISED, bg='#cccccc')
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.table_frame = ttk.LabelFrame(self.paned_window, text="Tabelle", padding="5")
        self.paned_window.add(self.table_frame, minsize=300)

        self.plot_frame = ttk.LabelFrame(self.paned_window, text="Diagramm", padding="5")
        self.paned_window.add(self.plot_frame, minsize=300)

    def get_main_frame(self):
        """Gibt den Haupt-Frame zurück"""
        return self.main_frame

    def get_filter_frame(self):
        """Gibt den Filter-Frame zurück"""
        return self.filter_frame

    def get_paned_window(self):
        """Gibt das PanedWindow zurück"""
        return self.paned_window

    def get_table_frame(self):
        """Gibt den Tabellen-Frame zurück"""
        return self.table_frame

    def get_plot_frame(self):
        """Gibt den Plot-Frame zurück"""
        return self.plot_frame
