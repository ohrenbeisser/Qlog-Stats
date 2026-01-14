"""
Context Menu Module für Qlog-Stats
Verwaltet das Rechtsklick-Kontextmenü für Tabellen
"""

import tkinter as tk
from tkinter import ttk
import webbrowser


class ContextMenu:
    """Verwaltet das Kontextmenü für QSO-Tabellen"""

    def __init__(self, tree_widget, db, parent_window):
        """
        Initialisiert das Kontextmenü

        Args:
            tree_widget: Treeview-Widget
            db: QlogDatabase Instanz
            parent_window: Parent-Fenster für Dialoge
        """
        self.tree = tree_widget
        self.db = db
        self.parent = parent_window
        self.menu = None
        self._create_menu()
        self._bind_events()

    def _create_menu(self):
        """Erstellt das Kontextmenü"""
        self.menu = tk.Menu(self.tree, tearoff=0)
        self.menu.add_command(label="Details", command=self._show_details)
        self.menu.add_separator()
        self.menu.add_command(label="QRZ.com öffnen", command=self._open_qrz)
        self.menu.add_command(label="Grid auf Karte", command=self._open_grid)

    def _bind_events(self):
        """Bindet das Kontextmenü an Rechtsklick"""
        # Rechtsklick (Button-3 auf Linux/Windows, Button-2 auf Mac)
        self.tree.bind("<Button-3>", self._show_menu)
        # Für Mac
        self.tree.bind("<Button-2>", self._show_menu)

    def _show_menu(self, event):
        """Zeigt das Kontextmenü an der Cursor-Position"""
        # Identifiziere die angeklickte Zeile
        row_id = self.tree.identify_row(event.y)
        if row_id:
            # Selektiere die Zeile
            self.tree.selection_set(row_id)
            # Zeige Menü
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()

    def _get_selected_callsign(self):
        """
        Holt das Rufzeichen der ausgewählten Zeile

        Returns:
            str: Rufzeichen oder None
        """
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            if values:
                # Callsign ist immer die erste Spalte
                return values[0]
        return None

    def _show_details(self):
        """Zeigt den Details-Dialog für das ausgewählte QSO"""
        callsign = self._get_selected_callsign()
        if not callsign:
            return

        # Hole ALLE QSO-Details aus der Datenbank
        # Wir brauchen mehr Kontext - welches spezifische QSO wurde ausgewählt?
        # Für jetzt: Hole das erste QSO mit diesem Rufzeichen
        # TODO: Verbessern durch eindeutige ID

        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        values = item['values']

        # Hole alle Spalten-Namen
        columns = self.tree['columns']

        # Erstelle Dictionary aus Spalten und Werten
        qso_data = {}
        for i, col in enumerate(columns):
            if i < len(values):
                qso_data[col] = values[i]

        # Zeige Details-Dialog
        DetailsDialog(self.parent, qso_data, callsign, self.db).show()

    def _open_qrz(self):
        """Öffnet QRZ.com für das ausgewählte Rufzeichen"""
        callsign = self._get_selected_callsign()
        if callsign:
            url = f"https://www.qrz.com/db/{callsign}"
            webbrowser.open(url)

    def _open_grid(self):
        """Öffnet Google Maps mit dem Grid/Locator"""
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        values = item['values']
        columns = self.tree['columns']

        # Suche nach gridsquare in den Spalten
        gridsquare = None
        for i, col in enumerate(columns):
            if col == 'gridsquare' and i < len(values):
                gridsquare = values[i]
                break

        if not gridsquare or gridsquare == '':
            # Versuche aus Datenbank zu holen
            callsign = values[0] if values else None
            if callsign:
                gridsquare = self._get_gridsquare_from_db(callsign)

        if gridsquare and gridsquare != '':
            self._open_grid_in_maps(gridsquare)
        else:
            from tkinter import messagebox
            messagebox.showinfo("Grid nicht verfügbar",
                              "Für dieses QSO ist kein Locator/Grid verfügbar.",
                              parent=self.parent)

    def _get_gridsquare_from_db(self, callsign):
        """
        Holt den Gridsquare aus der Datenbank

        Args:
            callsign: Rufzeichen

        Returns:
            str: Gridsquare oder None
        """
        try:
            query = "SELECT gridsquare FROM contacts WHERE callsign = ? LIMIT 1"
            result = self.db.execute_query(query, (callsign,))
            if result:
                return result[0].get('gridsquare', '')
        except:
            pass
        return None

    @staticmethod
    def _open_grid_in_maps(gridsquare):
        """
        Öffnet Google Maps mit dem Gridsquare/Locator

        Args:
            gridsquare: Maidenhead Locator (z.B. JO62qm)
        """
        # Konvertiere Maidenhead Locator zu Koordinaten (ungefähre Mitte des Quadrats)
        lat, lon = ContextMenu._maidenhead_to_latlon(gridsquare)

        if lat is not None and lon is not None:
            # Google Maps URL
            url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            webbrowser.open(url)

    @staticmethod
    def _maidenhead_to_latlon(locator):
        """
        Konvertiert Maidenhead Locator zu Lat/Lon (Zentrum des Quadrats)

        Args:
            locator: Maidenhead Locator (z.B. JO62qm)

        Returns:
            tuple: (latitude, longitude) oder (None, None) bei Fehler
        """
        try:
            locator = locator.upper().strip()

            # Mindestens 4 Zeichen erforderlich
            if len(locator) < 4:
                return None, None

            # Field (erste 2 Buchstaben)
            lon = (ord(locator[0]) - ord('A')) * 20 - 180
            lat = (ord(locator[1]) - ord('A')) * 10 - 90

            # Square (nächste 2 Ziffern)
            lon += int(locator[2]) * 2
            lat += int(locator[3]) * 1

            # Subsquare (optional, nächste 2 Buchstaben)
            if len(locator) >= 6:
                lon += (ord(locator[4]) - ord('A')) * (2/24) + (2/24/2)  # Mitte
                lat += (ord(locator[5]) - ord('A')) * (1/24) + (1/24/2)  # Mitte
            else:
                # Mitte des Squares
                lon += 1
                lat += 0.5

            return lat, lon

        except Exception:
            return None, None


class DetailsDialog:
    """Dialog zur Anzeige aller QSO-Details"""

    def __init__(self, parent, qso_data, callsign, db):
        """
        Initialisiert den Details-Dialog

        Args:
            parent: Parent-Fenster
            qso_data: Dictionary mit aktuell angezeigten QSO-Daten
            callsign: Rufzeichen
            db: QlogDatabase Instanz
        """
        self.parent = parent
        self.qso_data = qso_data
        self.callsign = callsign
        self.db = db
        self.dialog = None

        # Hole vollständige Daten aus DB
        self.full_data = self._get_full_qso_data()

    def _get_full_qso_data(self):
        """
        Holt ALLE Felder für das QSO aus der Datenbank

        Returns:
            dict: Vollständige QSO-Daten
        """
        try:
            # Versuche das QSO über Datum/Zeit zu identifizieren (wenn vorhanden)
            date = self.qso_data.get('date', '')
            time = self.qso_data.get('time', '')

            if date and time:
                query = """
                    SELECT * FROM contacts
                    WHERE callsign = ?
                    AND DATE(start_time) = ?
                    AND TIME(start_time) = ?
                    LIMIT 1
                """
                result = self.db.execute_query(query, (self.callsign, date, time))
            else:
                # Fallback: Hole erstes QSO mit diesem Rufzeichen
                query = "SELECT * FROM contacts WHERE callsign = ? LIMIT 1"
                result = self.db.execute_query(query, (self.callsign,))

            if result:
                return result[0]

        except Exception as e:
            print(f"Fehler beim Laden der QSO-Details: {e}")

        return {}

    def show(self):
        """Zeigt den Details-Dialog an"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"QSO-Details: {self.callsign}")
        self.dialog.geometry("700x600")
        self.dialog.resizable(True, True)

        # Zentriere das Fenster
        self.dialog.transient(self.parent)

        self._create_widgets()

        # Zentriere das Fenster auf dem Hauptfenster
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

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

        # Importiere Spalten-Labels
        from ui.table_columns import get_column_label

        # Zeige alle Felder
        row = 0
        for field, value in sorted(self.full_data.items()):
            if value is not None and value != '':
                # Label
                label = ttk.Label(scrollable_frame,
                                text=f"{get_column_label(field)}:",
                                font=('TkDefaultFont', 9, 'bold'))
                label.grid(row=row, column=0, sticky='w', padx=(0, 10), pady=2)

                # Wert
                value_label = ttk.Label(scrollable_frame,
                                       text=str(value),
                                       font=('TkDefaultFont', 9))
                value_label.grid(row=row, column=1, sticky='w', pady=2)

                row += 1

        # Schließen-Button
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(side="bottom", fill="x", padx=20, pady=10)

        close_btn = ttk.Button(button_frame, text="Schließen",
                              command=self.dialog.destroy, width=12)
        close_btn.pack(side="right")
