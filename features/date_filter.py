"""
Data Filter Module für Qlog-Stats
Verwaltet die Datumsfilter- und erweiterte Filter-Funktionalität
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta


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
        self.callsign_search_var = tk.StringVar()
        self.search_mode_var = tk.StringVar(value="partial")  # "exact" oder "partial"
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

        # Quick-Select Buttons für Zeiträume
        ttk.Button(date_frame, text="Jahr", width=6,
                  command=self._set_current_year).pack(side=tk.LEFT, padx=2)
        ttk.Button(date_frame, text="Monat", width=6,
                  command=self._set_current_month).pack(side=tk.LEFT, padx=2)
        ttk.Button(date_frame, text="Woche", width=6,
                  command=self._set_current_week).pack(side=tk.LEFT, padx=2)
        ttk.Button(date_frame, text="Tag", width=6,
                  command=self._set_current_day).pack(side=tk.LEFT, padx=2)

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

        # Dritte Zeile: Rufzeichen-Suche (initial unsichtbar)
        self.search_frame = ttk.Frame(self.parent_frame)
        # Nicht packen - wird erst bei Bedarf eingeblendet

        ttk.Label(self.search_frame, text="Rufzeichen:").pack(side=tk.LEFT, padx=(0, 5))
        self.callsign_search_entry = ttk.Entry(self.search_frame,
                                               textvariable=self.callsign_search_var,
                                               width=15)
        self.callsign_search_entry.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Radiobutton(self.search_frame, text="Teilstring", variable=self.search_mode_var,
                       value="partial").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(self.search_frame, text="Exakt", variable=self.search_mode_var,
                       value="exact").pack(side=tk.LEFT, padx=(0, 15))

        self.search_btn = ttk.Button(self.search_frame, text="Suchen",
                                     command=self._perform_search)
        self.search_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_search_btn = ttk.Button(self.search_frame, text="Suche löschen",
                                           command=self._clear_search)
        self.clear_search_btn.pack(side=tk.LEFT)

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

    def _set_current_year(self):
        """Setzt den Filter auf das aktuelle Jahr"""
        today = datetime.now()
        start_date = f"{today.year}-01-01"
        end_date = f"{today.year}-12-31"
        self.start_date_var.set(start_date)
        self.end_date_var.set(end_date)
        self.apply_filter()

    def _set_current_month(self):
        """Setzt den Filter auf den aktuellen Monat"""
        today = datetime.now()
        # Erster Tag des Monats
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        # Letzter Tag des Monats
        if today.month == 12:
            last_day = today.replace(day=31)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
            last_day = next_month - timedelta(days=1)
        end_date = last_day.strftime('%Y-%m-%d')
        self.start_date_var.set(start_date)
        self.end_date_var.set(end_date)
        self.apply_filter()

    def _set_current_week(self):
        """Setzt den Filter auf die aktuelle Woche (Montag-Sonntag)"""
        today = datetime.now()
        # Montag der aktuellen Woche (ISO Woche)
        monday = today - timedelta(days=today.weekday())
        # Sonntag der aktuellen Woche
        sunday = monday + timedelta(days=6)
        self.start_date_var.set(monday.strftime('%Y-%m-%d'))
        self.end_date_var.set(sunday.strftime('%Y-%m-%d'))
        self.apply_filter()

    def _set_current_day(self):
        """Setzt den Filter auf den heutigen Tag"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.start_date_var.set(today)
        self.end_date_var.set(today)
        self.apply_filter()

    def _perform_search(self):
        """Führt die Rufzeichen-Suche aus"""
        search_term = self.callsign_search_var.get().strip()
        if not search_term:
            return
        # Callback wird vom Controller gesetzt
        if hasattr(self, 'search_callback') and self.search_callback:
            self.search_callback()

    def _clear_search(self):
        """Löscht die Suche und setzt zurück"""
        self.callsign_search_var.set("")

    def get_search_params(self):
        """
        Gibt die Suchparameter zurück

        Returns:
            Dictionary mit search_term und search_mode oder None
        """
        search_term = self.callsign_search_var.get().strip()
        if not search_term:
            return None
        return {
            'search_term': search_term,
            'search_mode': self.search_mode_var.get()
        }

    def show_search_row(self):
        """Blendet die Rufzeichen-Suchzeile ein und setzt den Fokus"""
        self.search_frame.pack(fill=tk.X, pady=(5, 0))
        # Fokus auf das Eingabefeld setzen
        self.callsign_search_entry.focus_set()

    def hide_search_row(self):
        """Blendet die Rufzeichen-Suchzeile aus"""
        self.search_frame.pack_forget()

    def is_search_row_visible(self):
        """Prüft ob die Suchzeile sichtbar ist"""
        return self.search_frame.winfo_ismapped()
