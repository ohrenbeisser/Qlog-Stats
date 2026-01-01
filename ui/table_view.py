"""
Table View Module für Qlog-Stats
Verwaltet die Treeview-Tabelle mit Sortierung
"""

import tkinter as tk
from tkinter import ttk


class TableView:
    """Verwaltet die Treeview-Tabelle mit Sortierungs-Funktionalität"""

    def __init__(self, parent_frame):
        """
        Initialisiert die Table View

        Args:
            parent_frame: Tkinter Frame für die Tabelle
        """
        self.parent_frame = parent_frame
        self.tree = None
        self.scrollbar_y = None
        self.scrollbar_x = None
        self.sort_reverse = {}
        self.current_columns = []

        self._create_widgets()

    def _create_widgets(self):
        """Erstellt die Treeview und Scrollbars"""
        tree_scroll_frame = ttk.Frame(self.parent_frame)
        tree_scroll_frame.pack(fill=tk.BOTH, expand=True)

        self.scrollbar_y = ttk.Scrollbar(tree_scroll_frame, orient=tk.VERTICAL)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.scrollbar_x = ttk.Scrollbar(tree_scroll_frame, orient=tk.HORIZONTAL)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(tree_scroll_frame, show='tree headings',
                                yscrollcommand=self.scrollbar_y.set,
                                xscrollcommand=self.scrollbar_x.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar_y.config(command=self.tree.yview)
        self.scrollbar_x.config(command=self.tree.xview)

    def populate(self, columns, data, on_double_click=None):
        """
        Füllt die Tabelle mit Daten

        Args:
            columns: Liste der Spalten-Namen
            data: Liste von Dictionaries mit Daten
            on_double_click: Optionaler Callback für Doppelklick
        """
        self.tree.delete(*self.tree.get_children())

        self.tree['columns'] = columns
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.current_columns = columns

        for col in columns:
            self.tree.heading(col, text=col.capitalize(), anchor=tk.W,
                            command=lambda c=col: self._sort_column(c))
            self.tree.column(col, anchor=tk.W, width=200)
            self.sort_reverse[col] = False

        for idx, row in enumerate(data, 1):
            values = [row.get(col, '') for col in columns]
            self.tree.insert('', tk.END, iid=idx, values=values)

        if on_double_click:
            self.tree.bind('<Double-Button-1>', on_double_click)
        else:
            self.tree.unbind('<Double-Button-1>')

    def _sort_column(self, col):
        """
        Sortiert die Tabelle nach einer Spalte

        Intelligente Sortierung:
        - Numerische Werte werden als Zahlen sortiert
        - Text wird alphabetisch (case-insensitive) sortiert
        - Sortierungs-Richtung wechselt bei jedem Klick
        - Visueller Indikator (▲/▼) zeigt aktuelle Sortierung

        Args:
            col: Spaltenname nach dem sortiert werden soll
        """
        # 1. Alle Zeilen mit ihren Werten für die Spalte holen
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]

        # 2. Sortieren mit intelligentem Key-Handling
        try:
            # Versuche numerische Sortierung für Zahlen, sonst alphabetisch
            items.sort(key=lambda x: float(x[0]) if x[0].replace('.', '', 1).replace('-', '', 1).isdigit() else x[0].lower(),
                      reverse=self.sort_reverse[col])
        except (ValueError, AttributeError):
            # Fallback: Reine String-Sortierung
            items.sort(key=lambda x: str(x[0]).lower(), reverse=self.sort_reverse[col])

        # 3. Treeview in neuer Reihenfolge anordnen
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)

        # 4. Sortier-Richtung für nächsten Klick umkehren
        self.sort_reverse[col] = not self.sort_reverse[col]

        # 5. Visuellen Indikator aktualisieren
        sort_indicator = ' ▼' if self.sort_reverse[col] else ' ▲'
        for c in self.current_columns:
            if c == col:
                # Sortierte Spalte mit Indikator
                self.tree.heading(c, text=c.capitalize() + sort_indicator)
            else:
                # Andere Spalten ohne Indikator
                self.tree.heading(c, text=c.capitalize())

    def set_label(self, text):
        """
        Setzt das Label des Parent-Frames (falls es ein LabelFrame ist)

        Args:
            text: Neuer Label-Text
        """
        if isinstance(self.parent_frame, ttk.LabelFrame):
            self.parent_frame.config(text=text)

    def get_tree(self):
        """Gibt das Treeview-Widget zurück"""
        return self.tree
