"""
Date Filter Module für Qlog-Stats
Verwaltet die Datumsfilter-Funktionalität
"""

import tkinter as tk
from tkinter import ttk


class DateFilter:
    """Verwaltet die Datumsfilter UI und Logik"""

    def __init__(self, parent_frame, db, on_filter_change_callback):
        """
        Initialisiert den Date Filter

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
        self.filter_info_label = None

        self._create_widgets()
        self._load_date_range()

    def _create_widgets(self):
        """Erstellt die Filter-Widgets"""
        ttk.Label(self.parent_frame, text="Von:").pack(side=tk.LEFT, padx=(0, 5))
        self.start_date_entry = ttk.Entry(self.parent_frame,
                                         textvariable=self.start_date_var, width=12)
        self.start_date_entry.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(self.parent_frame, text="Bis:").pack(side=tk.LEFT, padx=(0, 5))
        self.end_date_entry = ttk.Entry(self.parent_frame,
                                       textvariable=self.end_date_var, width=12)
        self.end_date_entry.pack(side=tk.LEFT, padx=(0, 20))

        self.apply_filter_btn = ttk.Button(self.parent_frame, text="Filter anwenden",
                                          command=self.apply_filter)
        self.apply_filter_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.reset_filter_btn = ttk.Button(self.parent_frame, text="Zurücksetzen",
                                          command=self.reset_filter)
        self.reset_filter_btn.pack(side=tk.LEFT, padx=(0, 20))

        self.filter_info_label = ttk.Label(self.parent_frame, text="")
        self.filter_info_label.pack(side=tk.LEFT, padx=(20, 0))

    def _load_date_range(self):
        """Lädt den Datumsbereich aus der Datenbank"""
        if self.db:
            date_range = self.db.get_date_range()
            self.start_date_var.set(date_range['min_date'])
            self.end_date_var.set(date_range['max_date'])
            self.update_info()

    def get_dates(self):
        """
        Gibt das aktuelle Start- und End-Datum zurück

        Returns:
            Tuple (start_date, end_date)
        """
        return self.start_date_var.get(), self.end_date_var.get()

    def update_info(self):
        """Aktualisiert die Filter-Info-Anzeige"""
        start_date, end_date = self.get_dates()

        if self.db:
            total = self.db.get_total_qsos(start_date, end_date)
            self.filter_info_label.config(text=f"QSOs: {total:,}")

    def apply_filter(self):
        """Wendet den Filter an und ruft den Callback auf"""
        self.update_info()
        if self.on_filter_change:
            self.on_filter_change()

    def reset_filter(self):
        """Setzt den Filter auf den Datenbank-Bereich zurück"""
        self._load_date_range()
        self.apply_filter()
