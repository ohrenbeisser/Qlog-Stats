"""
Settings Dialog Module für Qlog-Stats
Verwaltet den Einstellungs-Dialog mit Tabs
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os


class SettingsDialog:
    """Dialog für Anwendungseinstellungen mit Tabs"""

    def __init__(self, parent, config_manager, db=None, on_db_change_callback=None, on_columns_change_callback=None):
        """
        Initialisiert den Einstellungs-Dialog

        Args:
            parent: Parent-Fenster
            config_manager: ConfigManager Instanz
            db: Datenbank-Instanz für Spalten-Auslesen
            on_db_change_callback: Callback wenn DB-Pfad geändert wird
            on_columns_change_callback: Callback wenn Spalten geändert wurden
        """
        self.parent = parent
        self.config = config_manager
        self.db = db
        self.on_db_change_callback = on_db_change_callback
        self.on_columns_change_callback = on_columns_change_callback
        self.dialog = None
        self.result = False

        # Variablen für Pfade-Tab
        self.db_path_var = None

        # Variablen für Design-Tab
        self.theme_var = None
        self.theme_mode_var = None

        # Variablen für Felder-Tab
        self.available_listbox = None
        self.selected_listbox = None
        self.all_db_columns = []

    def show(self):
        """Zeigt den Einstellungs-Dialog an"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Einstellungen")
        self.dialog.geometry("750x600")
        self.dialog.resizable(True, True)
        self.dialog.minsize(600, 500)

        bg_color = self._get_bg_color()
        self.dialog.configure(bg=bg_color)

        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        self._create_widgets()
        self._load_current_settings()
        self._center_dialog()

        self.dialog.wait_window()
        return self.result

    def _get_bg_color(self):
        """Gibt die Hintergrundfarbe basierend auf dem Theme zurück"""
        theme_mode = self.config.get_theme_mode()
        return '#2b2b2b' if theme_mode == 'dark' else 'white'

    def _create_widgets(self):
        """Erstellt die Widgets des Dialogs"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook (Tabs) erstellen
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Tab 1: Pfade
        self.paths_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.paths_frame, text="Pfade")
        self._create_paths_tab()

        # Tab 2: Design
        self.design_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.design_frame, text="Design")
        self._create_design_tab()

        # Tab 3: Felder
        self.fields_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.fields_frame, text="Felder")
        self._create_fields_tab()

        # Button-Frame unten
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Abbrechen", command=self._on_cancel, width=12).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Speichern", command=self._on_save, width=12).pack(side=tk.RIGHT)

    def _create_paths_tab(self):
        """Erstellt den Pfade-Tab"""
        frame = self.paths_frame

        # Datenbank-Pfad
        ttk.Label(frame, text="Datenbank-Pfad:", font=('TkDefaultFont', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=(0, 5))
        ttk.Label(frame, text="Pfad zur QLog-Datenbank (qlog.db)", font=('TkDefaultFont', 8)).grid(
            row=1, column=0, sticky='w', pady=(0, 5))

        db_frame = ttk.Frame(frame)
        db_frame.grid(row=2, column=0, sticky='ew', pady=(0, 30))
        db_frame.columnconfigure(0, weight=1)

        self.db_path_var = tk.StringVar()
        ttk.Entry(db_frame, textvariable=self.db_path_var, width=60).grid(row=0, column=0, sticky='ew', padx=(0, 10))
        ttk.Button(db_frame, text="Durchsuchen...", command=self._browse_database).grid(row=0, column=1)

        frame.columnconfigure(0, weight=1)

    def _create_design_tab(self):
        """Erstellt den Design-Tab"""
        frame = self.design_frame

        # Theme-Auswahl
        ttk.Label(frame, text="Erscheinungsbild:", font=('TkDefaultFont', 10, 'bold')).grid(
            row=0, column=0, columnspan=4, sticky='w', pady=(0, 15))

        # Theme
        ttk.Label(frame, text="Theme:").grid(row=1, column=0, sticky='w', padx=(0, 10))
        self.theme_var = tk.StringVar()
        theme_combo = ttk.Combobox(frame, textvariable=self.theme_var,
                                   values=['Azure', 'Standard'], state='readonly', width=20)
        theme_combo.grid(row=1, column=1, sticky='w', padx=(0, 30))

        # Theme-Modus
        ttk.Label(frame, text="Modus:").grid(row=1, column=2, sticky='w', padx=(0, 10))
        self.theme_mode_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.theme_mode_var,
                    values=['Hell', 'Dunkel'], state='readonly', width=15).grid(row=1, column=3, sticky='w')

        # Hinweis
        ttk.Label(frame, text="Hinweis: Theme-Änderungen erfordern einen Neustart der Anwendung.",
                 font=('TkDefaultFont', 8)).grid(row=2, column=0, columnspan=4, sticky='w', pady=(20, 0))

    def _create_fields_tab(self):
        """Erstellt den Felder-Tab mit Dual-Listbox und Sortierung"""
        frame = self.fields_frame

        ttk.Label(frame, text="Spalten für Detail-Tabellen:", font=('TkDefaultFont', 10, 'bold')).grid(
            row=0, column=0, columnspan=5, sticky='w', pady=(0, 5))
        ttk.Label(frame, text="Wählen Sie Felder aus und ordnen Sie sie in der gewünschten Reihenfolge an.",
                 font=('TkDefaultFont', 8)).grid(row=1, column=0, columnspan=5, sticky='w', pady=(0, 10))

        # Linke Seite: Verfügbare Felder
        ttk.Label(frame, text="Verfügbare Felder:").grid(row=2, column=0, sticky='w')

        avail_frame = ttk.Frame(frame)
        avail_frame.grid(row=3, column=0, sticky='nsew', padx=(0, 5))

        avail_scroll = ttk.Scrollbar(avail_frame)
        avail_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.available_listbox = tk.Listbox(avail_frame, width=25, height=18, selectmode=tk.EXTENDED,
                                            yscrollcommand=avail_scroll.set)
        self.available_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        avail_scroll.config(command=self.available_listbox.yview)
        self.available_listbox.bind('<Double-Button-1>', lambda e: self._add_selected())

        # Mittlere Buttons (Hinzufügen/Entfernen)
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=1, padx=5)

        ttk.Button(btn_frame, text=">>", command=self._add_selected, width=4).pack(pady=2)
        ttk.Button(btn_frame, text="<<", command=self._remove_selected, width=4).pack(pady=2)
        ttk.Button(btn_frame, text="Alle >>", command=self._add_all, width=6).pack(pady=(20, 2))
        ttk.Button(btn_frame, text="<< Alle", command=self._remove_all, width=6).pack(pady=2)

        # Rechte Seite: Ausgewählte Felder
        ttk.Label(frame, text="Ausgewählte Felder (Reihenfolge):").grid(row=2, column=2, sticky='w')

        sel_frame = ttk.Frame(frame)
        sel_frame.grid(row=3, column=2, sticky='nsew', padx=(5, 5))

        sel_scroll = ttk.Scrollbar(sel_frame)
        sel_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.selected_listbox = tk.Listbox(sel_frame, width=25, height=18, selectmode=tk.SINGLE,
                                           yscrollcommand=sel_scroll.set)
        self.selected_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sel_scroll.config(command=self.selected_listbox.yview)
        self.selected_listbox.bind('<Double-Button-1>', lambda e: self._remove_selected())

        # Drag & Drop Bindings
        self.selected_listbox.bind('<Button-1>', self._on_drag_start)
        self.selected_listbox.bind('<B1-Motion>', self._on_drag_motion)
        self.selected_listbox.bind('<ButtonRelease-1>', self._on_drag_end)
        self._drag_data = {'index': None}

        # Sortier-Buttons (rechts)
        sort_frame = ttk.Frame(frame)
        sort_frame.grid(row=3, column=3, padx=5)

        ttk.Button(sort_frame, text="▲", command=self._move_up, width=3).pack(pady=2)
        ttk.Button(sort_frame, text="▼", command=self._move_down, width=3).pack(pady=2)
        ttk.Button(sort_frame, text="⬆", command=self._move_top, width=3).pack(pady=(20, 2))
        ttk.Button(sort_frame, text="⬇", command=self._move_bottom, width=3).pack(pady=2)

        # Info-Text
        ttk.Label(frame, text="Tipp: Doppelklick zum Hinzufügen/Entfernen. Drag & Drop zum Sortieren.",
                 font=('TkDefaultFont', 8)).grid(row=4, column=0, columnspan=5, sticky='w', pady=(10, 0))
        ttk.Label(frame, text="Das Rufzeichen ist immer an erster Stelle und kann nicht entfernt werden.",
                 font=('TkDefaultFont', 8)).grid(row=5, column=0, columnspan=5, sticky='w')

        # Grid-Konfiguration
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(3, weight=1)

    def _load_current_settings(self):
        """Lädt die aktuellen Einstellungen"""
        # Pfade
        self.db_path_var.set(self.config.get_db_path())

        # Design
        theme = self.config.get_theme()
        theme_mode = self.config.get_theme_mode()
        self.theme_var.set('Azure' if theme == 'azure' else 'Standard')
        self.theme_mode_var.set('Dunkel' if theme_mode == 'dark' else 'Hell')

        # Felder laden
        self._load_database_columns()
        self._load_column_selection()

    def _load_database_columns(self):
        """Lädt alle verfügbaren Spalten aus der Datenbank"""
        self.all_db_columns = []

        if self.db:
            try:
                columns = self.db.get_table_columns()
                for col in columns:
                    col_name = col['name']
                    # ID-Spalte ausblenden
                    if col_name.lower() != 'id':
                        self.all_db_columns.append(col_name)
            except Exception as e:
                print(f"Fehler beim Laden der Spalten: {e}")

        # Fallback auf bekannte Spalten wenn DB nicht verfügbar
        if not self.all_db_columns:
            from ui.table_columns import AVAILABLE_COLUMNS
            self.all_db_columns = list(AVAILABLE_COLUMNS.keys())

    def _load_column_selection(self):
        """Lädt die Spalten-Auswahl in die Listboxen"""
        self.available_listbox.delete(0, tk.END)
        self.selected_listbox.delete(0, tk.END)

        # Aktuell konfigurierte Spalten
        configured = self.config.get_detail_columns()

        # Rufzeichen immer zuerst in ausgewählt
        self.selected_listbox.insert(tk.END, "callsign")

        # Restliche konfigurierte Spalten
        for col in configured:
            if col != 'callsign' and col in self.all_db_columns:
                self.selected_listbox.insert(tk.END, col)

        # Verfügbare Spalten (nicht ausgewählt, ohne callsign)
        for col in sorted(self.all_db_columns):
            if col not in configured and col != 'callsign':
                self.available_listbox.insert(tk.END, col)

    def _add_selected(self):
        """Fügt ausgewählte Felder hinzu"""
        selection = self.available_listbox.curselection()
        items = [self.available_listbox.get(i) for i in selection]
        for item in items:
            self.selected_listbox.insert(tk.END, item)
        for i in reversed(selection):
            self.available_listbox.delete(i)

    def _remove_selected(self):
        """Entfernt ausgewählte Felder (außer callsign)"""
        selection = self.selected_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        item = self.selected_listbox.get(idx)
        if item == 'callsign':
            messagebox.showinfo("Info", "Das Rufzeichen kann nicht entfernt werden.", parent=self.dialog)
            return
        self.selected_listbox.delete(idx)
        # In verfügbare Liste einfügen (sortiert)
        items = list(self.available_listbox.get(0, tk.END))
        items.append(item)
        items.sort()
        self.available_listbox.delete(0, tk.END)
        for i in items:
            self.available_listbox.insert(tk.END, i)

    def _add_all(self):
        """Fügt alle verfügbaren Felder hinzu"""
        items = list(self.available_listbox.get(0, tk.END))
        for item in items:
            self.selected_listbox.insert(tk.END, item)
        self.available_listbox.delete(0, tk.END)

    def _remove_all(self):
        """Entfernt alle Felder außer callsign"""
        items = list(self.selected_listbox.get(0, tk.END))
        self.selected_listbox.delete(0, tk.END)
        self.selected_listbox.insert(tk.END, 'callsign')

        available = []
        for item in items:
            if item != 'callsign':
                available.append(item)
        available.sort()
        for item in available:
            self.available_listbox.insert(tk.END, item)

    def _move_up(self):
        """Bewegt ausgewähltes Feld nach oben"""
        selection = self.selected_listbox.curselection()
        if not selection or selection[0] <= 1:  # 0 ist callsign
            return
        idx = selection[0]
        item = self.selected_listbox.get(idx)
        self.selected_listbox.delete(idx)
        self.selected_listbox.insert(idx - 1, item)
        self.selected_listbox.selection_set(idx - 1)

    def _move_down(self):
        """Bewegt ausgewähltes Feld nach unten"""
        selection = self.selected_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        if idx == 0 or idx >= self.selected_listbox.size() - 1:
            return
        item = self.selected_listbox.get(idx)
        self.selected_listbox.delete(idx)
        self.selected_listbox.insert(idx + 1, item)
        self.selected_listbox.selection_set(idx + 1)

    def _move_top(self):
        """Bewegt ausgewähltes Feld ganz nach oben (nach callsign)"""
        selection = self.selected_listbox.curselection()
        if not selection or selection[0] <= 1:
            return
        idx = selection[0]
        item = self.selected_listbox.get(idx)
        self.selected_listbox.delete(idx)
        self.selected_listbox.insert(1, item)
        self.selected_listbox.selection_set(1)

    def _move_bottom(self):
        """Bewegt ausgewähltes Feld ganz nach unten"""
        selection = self.selected_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        idx = selection[0]
        if idx >= self.selected_listbox.size() - 1:
            return
        item = self.selected_listbox.get(idx)
        self.selected_listbox.delete(idx)
        self.selected_listbox.insert(tk.END, item)
        self.selected_listbox.selection_set(self.selected_listbox.size() - 1)

    def _on_drag_start(self, event):
        """Startet Drag & Drop"""
        idx = self.selected_listbox.nearest(event.y)
        if idx > 0:  # Nicht callsign
            self._drag_data['index'] = idx

    def _on_drag_motion(self, event):
        """Drag & Drop Bewegung"""
        if self._drag_data['index'] is None:
            return
        idx = self.selected_listbox.nearest(event.y)
        if idx > 0 and idx != self._drag_data['index']:
            item = self.selected_listbox.get(self._drag_data['index'])
            self.selected_listbox.delete(self._drag_data['index'])
            self.selected_listbox.insert(idx, item)
            self._drag_data['index'] = idx

    def _on_drag_end(self, event):
        """Beendet Drag & Drop"""
        if self._drag_data['index'] is not None:
            self.selected_listbox.selection_clear(0, tk.END)
            self.selected_listbox.selection_set(self._drag_data['index'])
        self._drag_data['index'] = None

    def _browse_database(self):
        """Öffnet Datei-Dialog für Datenbank-Auswahl"""
        initial_dir = os.path.dirname(self.db_path_var.get()) or os.path.expanduser('~')
        filename = filedialog.askopenfilename(
            parent=self.dialog,
            title="Qlog-Datenbank auswählen",
            initialdir=initial_dir,
            filetypes=[("SQLite Datenbank", "*.db"), ("Alle Dateien", "*.*")]
        )
        if filename:
            self.db_path_var.set(filename)

    def _center_dialog(self):
        """Zentriert den Dialog auf dem Hauptfenster"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def _on_save(self):
        """Speichert die Einstellungen"""
        db_path = self.db_path_var.get().strip()

        # Validierung
        if not db_path:
            messagebox.showerror("Fehler", "Bitte geben Sie einen Datenbank-Pfad an.", parent=self.dialog)
            return

        if not os.path.exists(db_path):
            if not messagebox.askyesno("Warnung",
                f"Die Datenbank existiert nicht:\n{db_path}\n\nTrotzdem speichern?", parent=self.dialog):
                return

        # Spalten validieren
        selected_columns = list(self.selected_listbox.get(0, tk.END))
        if len(selected_columns) < 2:
            messagebox.showwarning("Warnung", "Bitte wählen Sie mindestens eine Spalte zusätzlich zum Rufzeichen.",
                                  parent=self.dialog)
            return

        # Alte Werte merken
        old_db_path = self.config.get_db_path()
        old_columns = self.config.get_detail_columns()
        old_theme = self.config.get_theme()
        old_theme_mode = self.config.get_theme_mode()

        # Speichern
        self.config.set_db_path(db_path)
        self.config.set_detail_columns(selected_columns)

        theme = 'azure' if self.theme_var.get() == 'Azure' else 'default'
        theme_mode = 'dark' if self.theme_mode_var.get() == 'Dunkel' else 'light'
        self.config.set_theme(theme, theme_mode)

        self.result = True
        self.dialog.destroy()

        # Callbacks
        if old_db_path != db_path and self.on_db_change_callback:
            self.on_db_change_callback()

        if old_columns != selected_columns and self.on_columns_change_callback:
            self.on_columns_change_callback()

        if old_theme != theme or old_theme_mode != theme_mode:
            messagebox.showinfo("Neustart erforderlich",
                "Die Theme-Einstellung wurde gespeichert.\n\n"
                "Bitte starten Sie die Anwendung neu.")

    def _on_cancel(self):
        """Schließt den Dialog ohne zu speichern"""
        self.result = False
        self.dialog.destroy()
