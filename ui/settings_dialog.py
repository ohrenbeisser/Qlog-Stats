"""
Settings Dialog Module für Qlog-Stats
Verwaltet den Einstellungs-Dialog
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os


class SettingsDialog:
    """Dialog für Anwendungseinstellungen"""

    def __init__(self, parent, config_manager, on_db_change_callback=None, on_columns_change_callback=None):
        """
        Initialisiert den Einstellungs-Dialog

        Args:
            parent: Parent-Fenster
            config_manager: ConfigManager Instanz
            on_db_change_callback: Callback wenn DB-Pfad geändert wird
            on_columns_change_callback: Callback wenn Spalten geändert wurden
        """
        self.parent = parent
        self.config = config_manager
        self.on_db_change_callback = on_db_change_callback
        self.on_columns_change_callback = on_columns_change_callback
        self.dialog = None
        self.db_path_var = None
        self.export_dir_var = None
        self.theme_var = None
        self.theme_mode_var = None
        self.column_vars = {}  # Dictionary für Spalten-Checkboxen
        self.result = False

    def show(self):
        """
        Zeigt den Einstellungs-Dialog an

        Returns:
            bool: True wenn Einstellungen gespeichert wurden
        """
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Einstellungen")
        self.dialog.geometry("700x650")
        self.dialog.resizable(True, True)

        # Zentriere das Fenster auf dem Hauptfenster
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        self._create_widgets()
        self._load_current_settings()

        # Warte auf Schließen des Dialogs
        self.dialog.wait_window()

        return self.result

    def _create_widgets(self):
        """Erstellt die Widgets des Dialogs"""
        # Canvas für Scrolling
        canvas = tk.Canvas(self.dialog, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)

        # Scrollbares Frame
        scrollable_frame = ttk.Frame(canvas, padding="20")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Maus-Scroll-Support
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        main_frame = scrollable_frame

        # Datenbank-Pfad
        db_label = ttk.Label(main_frame, text="Datenbank-Pfad:",
                            font=('TkDefaultFont', 10, 'bold'))
        db_label.grid(row=0, column=0, sticky='w', pady=(0, 5))

        db_frame = ttk.Frame(main_frame)
        db_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        db_frame.columnconfigure(0, weight=1)

        self.db_path_var = tk.StringVar()
        db_entry = ttk.Entry(db_frame, textvariable=self.db_path_var, width=50)
        db_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))

        db_browse_btn = ttk.Button(db_frame, text="Durchsuchen...",
                                   command=self._browse_database)
        db_browse_btn.grid(row=0, column=1)

        # Export-Verzeichnis
        export_label = ttk.Label(main_frame, text="Export-Verzeichnis:",
                                font=('TkDefaultFont', 10, 'bold'))
        export_label.grid(row=2, column=0, sticky='w', pady=(0, 5))

        export_frame = ttk.Frame(main_frame)
        export_frame.grid(row=3, column=0, sticky='ew', pady=(0, 20))
        export_frame.columnconfigure(0, weight=1)

        self.export_dir_var = tk.StringVar()
        export_entry = ttk.Entry(export_frame, textvariable=self.export_dir_var, width=50)
        export_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))

        export_browse_btn = ttk.Button(export_frame, text="Durchsuchen...",
                                       command=self._browse_export_dir)
        export_browse_btn.grid(row=0, column=1)

        # Theme-Auswahl
        theme_label = ttk.Label(main_frame, text="Erscheinungsbild:",
                               font=('TkDefaultFont', 10, 'bold'))
        theme_label.grid(row=4, column=0, sticky='w', pady=(0, 5))

        theme_frame = ttk.Frame(main_frame)
        theme_frame.grid(row=5, column=0, sticky='w', pady=(0, 20))

        # Theme-Dropdown
        ttk.Label(theme_frame, text="Theme:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.theme_var = tk.StringVar()
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var,
                                   values=['Azure', 'Standard'],
                                   state='readonly', width=20)
        theme_combo.grid(row=0, column=1, padx=(0, 20))

        # Theme-Modus (Hell/Dunkel)
        ttk.Label(theme_frame, text="Modus:").grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.theme_mode_var = tk.StringVar()
        mode_combo = ttk.Combobox(theme_frame, textvariable=self.theme_mode_var,
                                 values=['Hell', 'Dunkel'],
                                 state='readonly', width=15)
        mode_combo.grid(row=0, column=3)

        # Hinweis
        theme_info = ttk.Label(main_frame,
                              text="Hinweis: Änderung des Themes erfordert einen Neustart der Anwendung.",
                              font=('TkDefaultFont', 8))
        theme_info.grid(row=6, column=0, sticky='w', pady=(0, 10))

        # Trennlinie
        ttk.Separator(main_frame, orient='horizontal').grid(row=7, column=0, sticky='ew', pady=20)

        # Spaltenauswahl für Detail-Tabellen
        columns_label = ttk.Label(main_frame, text="Spalten für Detail-Tabellen:",
                                 font=('TkDefaultFont', 10, 'bold'))
        columns_label.grid(row=8, column=0, sticky='w', pady=(0, 5))

        columns_info = ttk.Label(main_frame,
                                text="Wähle die Spalten aus, die in Tabellen mit QSO-Details angezeigt werden sollen:",
                                font=('TkDefaultFont', 8))
        columns_info.grid(row=9, column=0, sticky='w', pady=(0, 10))

        # Frame für Checkboxen (mit mehreren Spalten)
        columns_frame = ttk.Frame(main_frame)
        columns_frame.grid(row=10, column=0, sticky='ew', pady=(0, 20))

        # Importiere verfügbare Spalten
        from ui.table_columns import AVAILABLE_COLUMNS, get_column_label

        # Erstelle Checkboxen in 3 Spalten
        col = 0
        row = 0
        max_cols = 3

        for col_id, col_info in AVAILABLE_COLUMNS.items():
            var = tk.BooleanVar()
            self.column_vars[col_id] = var

            # Callsign ist erforderlich und daher deaktiviert
            state = 'disabled' if col_info['required'] else 'normal'

            cb = ttk.Checkbutton(columns_frame,
                               text=col_info['label'],
                               variable=var,
                               state=state)
            cb.grid(row=row, column=col, sticky='w', padx=(0, 20), pady=2)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # Button-Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, sticky='e', pady=(10, 0))

        cancel_btn = ttk.Button(button_frame, text="Abbrechen",
                               command=self._on_cancel, width=12)
        cancel_btn.grid(row=0, column=0, padx=(0, 10))

        save_btn = ttk.Button(button_frame, text="Speichern",
                             command=self._on_save, width=12)
        save_btn.grid(row=0, column=1)

        # Spalte 0 dehnt sich aus
        main_frame.columnconfigure(0, weight=1)

        # Zentriere das Fenster auf dem Hauptfenster
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def _load_current_settings(self):
        """Lädt die aktuellen Einstellungen in die Felder"""
        self.db_path_var.set(self.config.get_db_path())
        self.export_dir_var.set(self.config.get_export_directory())

        # Lade Theme-Einstellungen
        theme = self.config.get_theme()
        theme_mode = self.config.get_theme_mode()

        # Setze Theme-Dropdown
        if theme == 'azure':
            self.theme_var.set('Azure')
        else:
            self.theme_var.set('Standard')

        # Setze Theme-Modus
        if theme_mode == 'dark':
            self.theme_mode_var.set('Dunkel')
        else:
            self.theme_mode_var.set('Hell')

        # Lade konfigurierte Spalten
        configured_columns = self.config.get_detail_columns()

        # Setze Checkboxen entsprechend
        for col_id, var in self.column_vars.items():
            var.set(col_id in configured_columns)

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

    def _browse_export_dir(self):
        """Öffnet Verzeichnis-Dialog für Export-Verzeichnis"""
        initial_dir = self.export_dir_var.get() or os.path.expanduser('~')
        directory = filedialog.askdirectory(
            parent=self.dialog,
            title="Export-Verzeichnis auswählen",
            initialdir=initial_dir
        )
        if directory:
            self.export_dir_var.set(directory)

    def _on_save(self):
        """Speichert die Einstellungen"""
        db_path = self.db_path_var.get().strip()
        export_dir = self.export_dir_var.get().strip()

        # Validierung
        if not db_path:
            messagebox.showerror("Fehler", "Bitte geben Sie einen Datenbank-Pfad an.",
                               parent=self.dialog)
            return

        if not os.path.exists(db_path):
            response = messagebox.askyesno(
                "Warnung",
                f"Die Datenbank existiert nicht:\n{db_path}\n\n"
                "Möchten Sie den Pfad trotzdem speichern?",
                parent=self.dialog
            )
            if not response:
                return

        # Speichere Einstellungen
        old_db_path = self.config.get_db_path()
        old_columns = self.config.get_detail_columns()

        self.config.set_db_path(db_path)

        if export_dir:
            # Erstelle Export-Verzeichnis falls es nicht existiert
            os.makedirs(export_dir, exist_ok=True)
            # Hier müsste man noch eine Methode in ConfigManager erstellen
            # Vorerst nur DB-Pfad speichern

        # Speichere ausgewählte Spalten
        selected_columns = [col_id for col_id, var in self.column_vars.items() if var.get()]

        # Validierung: Mindestens eine Spalte muss ausgewählt sein (außer callsign)
        if len(selected_columns) < 2:  # callsign + mindestens 1 weitere
            messagebox.showwarning("Warnung",
                                 "Bitte wählen Sie mindestens eine Spalte zusätzlich zu 'Rufzeichen' aus.",
                                 parent=self.dialog)
            return

        self.config.set_detail_columns(selected_columns)
        columns_changed = old_columns != self.config.get_detail_columns()

        # Speichere Theme-Einstellungen
        old_theme = self.config.get_theme()
        old_theme_mode = self.config.get_theme_mode()

        # Konvertiere Dropdown-Werte zu internen Werten
        theme = 'azure' if self.theme_var.get() == 'Azure' else 'default'
        theme_mode = 'dark' if self.theme_mode_var.get() == 'Dunkel' else 'light'

        self.config.set_theme(theme, theme_mode)
        theme_changed = (old_theme != theme or old_theme_mode != theme_mode)

        self.result = True

        # Dialog schließen
        self.dialog.destroy()

        # Rufe Callbacks auf
        if old_db_path != db_path and self.on_db_change_callback:
            self.on_db_change_callback()

        if columns_changed and self.on_columns_change_callback:
            self.on_columns_change_callback()

        # Informiere über Theme-Änderung
        if theme_changed:
            messagebox.showinfo(
                "Neustart erforderlich",
                "Die Theme-Einstellung wurde gespeichert.\n\n"
                "Bitte starten Sie die Anwendung neu, damit die Änderungen wirksam werden."
            )

    def _on_cancel(self):
        """Schließt den Dialog ohne zu speichern"""
        self.result = False
        self.dialog.destroy()
