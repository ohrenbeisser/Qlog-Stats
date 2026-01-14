"""
Query Manager Dialog für Qlog-Stats
Verwaltet gespeicherte Abfragen (Bearbeiten/Löschen)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable


class QueryManagerDialog:
    """Dialog zur Verwaltung gespeicherter Abfragen"""

    def __init__(self, parent, query_manager, on_change: Callable = None):
        """
        Initialisiert den Query Manager Dialog

        Args:
            parent: Parent-Fenster
            query_manager: QueryManager Instanz
            on_change: Callback wenn Abfragen geändert wurden
        """
        self.parent = parent
        self.query_manager = query_manager
        self.on_change = on_change

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Abfragen verwalten")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_widgets()
        self._load_queries()

    def _create_widgets(self):
        """Erstellt die Dialog-Widgets"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Info-Label
        ttk.Label(main_frame, text="Gespeicherte Abfragen:").pack(anchor=tk.W, pady=(0, 5))

        # Treeview mit Scrollbar (besser für Azure Theme)
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Verwende Treeview statt Listbox für besseres Theme-Support
        self.query_listbox = ttk.Treeview(list_frame, yscrollcommand=scrollbar.set,
                                         columns=('name',), show='tree', selectmode='browse')
        self.query_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.query_listbox.yview)

        # Bind Doppelklick
        self.query_listbox.bind('<Double-Button-1>', lambda e: self._edit_query())

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Bearbeiten",
                  command=self._edit_query).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Löschen",
                  command=self._delete_query).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Schließen",
                  command=self.dialog.destroy).pack(side=tk.RIGHT)

    def _load_queries(self):
        """Lädt alle gespeicherten Abfragen in die Liste"""
        # Lösche alle Einträge
        for item in self.query_listbox.get_children():
            self.query_listbox.delete(item)

        self.queries = self.query_manager.load_queries()

        if not self.queries:
            self.query_listbox.insert('', tk.END, text="(Keine Abfragen gespeichert)")
            return

        for i, query in enumerate(self.queries):
            name = query.get('name', 'Unbenannt')
            self.query_listbox.insert('', tk.END, iid=str(i), text=name)

    def _get_selected_query(self):
        """Gibt die aktuell ausgewählte Abfrage zurück"""
        selection = self.query_listbox.selection()
        if not selection:
            return None

        # Hole den Index aus der IID
        try:
            index = int(selection[0])
            if index >= len(self.queries):
                return None
            return self.queries[index]
        except (ValueError, IndexError):
            return None

    def _edit_query(self):
        """Bearbeitet die ausgewählte Abfrage"""
        query = self._get_selected_query()
        if not query:
            messagebox.showwarning("Warnung", "Bitte wählen Sie eine Abfrage aus.")
            return

        # Öffne Query Builder Dialog im Edit-Modus
        from .query_builder import QueryBuilderDialog
        dialog = QueryBuilderDialog(self.dialog, self.query_manager, existing_query=query)
        result = dialog.show()

        if result:
            self._load_queries()
            if self.on_change:
                self.on_change()

    def _delete_query(self):
        """Löscht die ausgewählte Abfrage"""
        query = self._get_selected_query()
        if not query:
            messagebox.showwarning("Warnung", "Bitte wählen Sie eine Abfrage aus.")
            return

        name = query.get('name', 'Unbenannt')
        confirm = messagebox.askyesno("Löschen bestätigen",
                                     f"Möchten Sie die Abfrage '{name}' wirklich löschen?")

        if confirm:
            query_id = query.get('id')
            if self.query_manager.delete_query(query_id):
                messagebox.showinfo("Erfolg", f"Abfrage '{name}' wurde gelöscht.")
                self._load_queries()
                if self.on_change:
                    self.on_change()
            else:
                messagebox.showerror("Fehler", "Fehler beim Löschen der Abfrage.")

    def show(self):
        """Zeigt den Dialog modal an"""
        self.dialog.wait_window()
