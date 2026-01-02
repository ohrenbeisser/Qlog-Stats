"""
Data Filter Module für Qlog-Stats
Verwaltet die Datumsfilter- und erweiterte Filter-Funktionalität
"""

import tkinter as tk
from tkinter import ttk


class DateFilter:
    """Verwaltet die Datumsfilter und erweiterte Filter (Band, Mode, Land) UI und Logik"""

    def __init__(self, parent_frame, db, on_filter_change_callback):
        """
        Initialisiert den Data Filter

        Args:
            parent_frame: Tkinter Frame für die Filter-Widgets
            db: QlogDatabase Instanz
            on_filter_change_callback: Callback der aufgerufen wird wenn Filter sich ändert
        """
        self.parent_frame = parent_frame
        self.db = db
        self.on_filter_change = on_filter_change_callback

        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        self.band_var = tk.StringVar(value="Alle")
        self.mode_var = tk.StringVar(value="Alle")
        self.country_var = tk.StringVar(value="Alle")
        self.filter_info_label = None

        self._create_widgets()
        self._load_date_range()

    def _create_widgets(self):
        """Erstellt die Filter-Widgets in zwei Zeilen"""
        # Erste Zeile: Datumsfilter
        date_frame = ttk.Frame(self.parent_frame)
        date_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(date_frame, text="Von:").pack(side=tk.LEFT, padx=(0, 5))
        self.start_date_entry = ttk.Entry(date_frame,
                                         textvariable=self.start_date_var, width=12)
        self.start_date_entry.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(date_frame, text="Bis:").pack(side=tk.LEFT, padx=(0, 5))
        self.end_date_entry = ttk.Entry(date_frame,
                                       textvariable=self.end_date_var, width=12)
        self.end_date_entry.pack(side=tk.LEFT, padx=(0, 20))

        # Zweite Zeile: Band/Mode/Land-Filter und Buttons
        filter_frame = ttk.Frame(self.parent_frame)
        filter_frame.pack(fill=tk.X)

        ttk.Label(filter_frame, text="Band:").pack(side=tk.LEFT, padx=(0, 5))
        self.band_combo = ttk.Combobox(filter_frame, textvariable=self.band_var,
                                      state="readonly", width=10)
        self.band_combo.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(filter_frame, text="Mode:").pack(side=tk.LEFT, padx=(0, 5))
        self.mode_combo = ttk.Combobox(filter_frame, textvariable=self.mode_var,
                                      state="readonly", width=10)
        self.mode_combo.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(filter_frame, text="Land:").pack(side=tk.LEFT, padx=(0, 5))
        self.country_combo = ttk.Combobox(filter_frame, textvariable=self.country_var,
                                         state="readonly", width=15)
        self.country_combo.pack(side=tk.LEFT, padx=(0, 20))

        self.apply_filter_btn = ttk.Button(filter_frame, text="Filter anwenden",
                                          command=self.apply_filter)
        self.apply_filter_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.reset_filter_btn = ttk.Button(filter_frame, text="Zurücksetzen",
                                          command=self.reset_filter)
        self.reset_filter_btn.pack(side=tk.LEFT, padx=(0, 20))

        self.filter_info_label = ttk.Label(filter_frame, text="")
        self.filter_info_label.pack(side=tk.LEFT, padx=(20, 0))

    def _load_date_range(self):
        """Lädt den Datumsbereich aus der Datenbank"""
        if self.db:
            date_range = self.db.get_date_range()
            self.start_date_var.set(date_range['min_date'])
            self.end_date_var.set(date_range['max_date'])
            self.update_info()

    def _load_filter_options(self):
        """Lädt die Filter-Optionen aus der Datenbank"""
        if not self.db:
            return

        try:
            # Bands laden
            bands = self.db.get_all_bands()
            self.band_combo['values'] = ['Alle'] + bands
            self.band_var.set('Alle')

            # Modes laden
            modes = self.db.get_all_modes()
            self.mode_combo['values'] = ['Alle'] + modes
            self.mode_var.set('Alle')

            # Countries laden
            countries = self.db.get_all_countries()
            self.country_combo['values'] = ['Alle'] + countries
            self.country_var.set('Alle')
        except Exception as e:
            print(f"Fehler beim Laden der Filter-Optionen: {e}")

    def get_dates(self):
        """
        Gibt das aktuelle Start- und End-Datum zurück

        Returns:
            Tuple (start_date, end_date)
        """
        return self.start_date_var.get(), self.end_date_var.get()

    def get_filters(self):
        """
        Gibt alle aktuellen Filter zurück

        Returns:
            Dictionary mit allen Filtern (start_date, end_date, band, mode, country)
        """
        return {
            'start_date': self.start_date_var.get(),
            'end_date': self.end_date_var.get(),
            'band': None if self.band_var.get() == 'Alle' else self.band_var.get(),
            'mode': None if self.mode_var.get() == 'Alle' else self.mode_var.get(),
            'country': None if self.country_var.get() == 'Alle' else self.country_var.get()
        }

    def update_info(self):
        """Aktualisiert die Filter-Info-Anzeige"""
        if self.db:
            filters = self.get_filters()
            total = self.db.get_total_qsos(**filters)
            self.filter_info_label.config(text=f"QSOs: {total:,}")

    def apply_filter(self):
        """Wendet den Filter an und ruft den Callback auf"""
        self.update_info()
        if self.on_filter_change:
            self.on_filter_change()

    def reset_filter(self):
        """Setzt den Filter auf den Datenbank-Bereich zurück"""
        self._load_date_range()
        self.band_var.set('Alle')
        self.mode_var.set('Alle')
        self.country_var.set('Alle')
        self.apply_filter()
