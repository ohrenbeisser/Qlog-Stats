"""
Query Builder Dialog für Qlog-Stats
Ermöglicht das Erstellen benutzerdefinierter Abfragen
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, List


class QueryBuilderDialog:
    """Dialog zum Erstellen und Bearbeiten von Abfragen"""

    # Verfügbare Datenbank-Felder
    DB_FIELDS = {
        'callsign': 'Rufzeichen',
        'start_time': 'Datum/Zeit',
        'band': 'Band',
        'mode': 'Mode',
        'country': 'Land',
        'rst_sent': 'RST gesendet',
        'rst_rcvd': 'RST empfangen',
        'name': 'Name',
        'qth': 'QTH',
        'gridsquare': 'Gridsquare',
        'comment': 'Kommentar',
        'freq': 'Frequenz',
        'tx_pwr': 'Sendeleistung',
        'dxcc': 'DXCC',
        'cont': 'Kontinent',
        'cqz': 'CQ Zone',
        'ituz': 'ITU Zone'
    }

    # Operatoren
    OPERATORS = {
        '=': 'gleich',
        '!=': 'ungleich',
        '>': 'größer',
        '<': 'kleiner',
        '>=': 'größer/gleich',
        '<=': 'kleiner/gleich',
        'LIKE': 'enthält',
        'NOT LIKE': 'enthält nicht',
        'IS NULL': 'ist leer',
        'IS NOT NULL': 'ist nicht leer'
    }

    # Standard-Spalten für Ergebnis
    DEFAULT_COLUMNS = ['callsign', 'start_time', 'band', 'mode', 'country']

    def __init__(self, parent, query_manager, existing_query: Optional[Dict] = None):
        """
        Initialisiert den Query Builder Dialog

        Args:
            parent: Parent-Fenster
            query_manager: QueryManager Instanz
            existing_query: Optionale bestehende Abfrage zum Bearbeiten
        """
        self.parent = parent
        self.query_manager = query_manager
        self.existing_query = existing_query
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Neue Abfrage" if not existing_query else "Abfrage bearbeiten")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Bedingungen-Liste
        self.conditions = []

        self._create_widgets()
        self._load_existing_query()

    def _create_widgets(self):
        """Erstellt die Dialog-Widgets"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Name der Abfrage
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(name_frame, text="Name der Abfrage:").pack(side=tk.LEFT)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=40)
        self.name_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)

        # Bedingungen
        conditions_frame = ttk.LabelFrame(main_frame, text="Bedingungen (alle mit AND verknüpft)", padding="10")
        conditions_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Scrollbarer Frame für Bedingungen
        canvas = tk.Canvas(conditions_frame, height=250)
        scrollbar = ttk.Scrollbar(conditions_frame, orient="vertical", command=canvas.yview)
        self.conditions_container = ttk.Frame(canvas)

        self.conditions_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.conditions_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Button zum Hinzufügen von Bedingungen
        add_btn_frame = ttk.Frame(conditions_frame)
        add_btn_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(add_btn_frame, text="+ Bedingung hinzufügen",
                  command=self._add_condition).pack(side=tk.LEFT)

        # Spaltenauswahl
        columns_frame = ttk.LabelFrame(main_frame, text="Anzuzeigende Spalten", padding="10")
        columns_frame.pack(fill=tk.X, pady=(0, 10))

        self.column_vars = {}
        col_grid_frame = ttk.Frame(columns_frame)
        col_grid_frame.pack(fill=tk.X)

        # 3 Spalten Layout
        row, col = 0, 0
        for field_id, field_name in self.DB_FIELDS.items():
            var = tk.BooleanVar(value=field_id in self.DEFAULT_COLUMNS)
            self.column_vars[field_id] = var

            cb = ttk.Checkbutton(col_grid_frame, text=field_name, variable=var)
            cb.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)

            col += 1
            if col >= 3:
                col = 0
                row += 1

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Speichern",
                  command=self._save_query).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Abbrechen",
                  command=self.dialog.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Vorschau SQL",
                  command=self._preview_sql).pack(side=tk.LEFT)

        # Erste Bedingung hinzufügen
        self._add_condition()

    def _add_condition(self):
        """Fügt eine neue Bedingung hinzu"""
        condition_frame = ttk.Frame(self.conditions_container)
        condition_frame.pack(fill=tk.X, pady=2)

        # Feld
        field_var = tk.StringVar()
        field_combo = ttk.Combobox(condition_frame, textvariable=field_var,
                                   values=list(self.DB_FIELDS.values()),
                                   state='readonly', width=15)
        field_combo.pack(side=tk.LEFT, padx=(0, 5))
        field_combo.current(0)

        # Operator
        operator_var = tk.StringVar()
        operator_combo = ttk.Combobox(condition_frame, textvariable=operator_var,
                                      values=list(self.OPERATORS.values()),
                                      state='readonly', width=15)
        operator_combo.pack(side=tk.LEFT, padx=(0, 5))
        operator_combo.current(0)

        # Wert
        value_var = tk.StringVar()
        value_entry = ttk.Entry(condition_frame, textvariable=value_var, width=20)
        value_entry.pack(side=tk.LEFT, padx=(0, 5))

        # Entfernen-Button
        remove_btn = ttk.Button(condition_frame, text="×", width=3,
                               command=lambda: self._remove_condition(condition_frame))
        remove_btn.pack(side=tk.LEFT)

        # Speichere Referenzen
        self.conditions.append({
            'frame': condition_frame,
            'field_var': field_var,
            'operator_var': operator_var,
            'value_var': value_var
        })

    def _remove_condition(self, frame):
        """Entfernt eine Bedingung"""
        # Finde und entferne aus Liste
        self.conditions = [c for c in self.conditions if c['frame'] != frame]
        frame.destroy()

    def _get_field_id(self, field_name: str) -> str:
        """Gibt die Feld-ID für einen Feldnamen zurück"""
        for field_id, name in self.DB_FIELDS.items():
            if name == field_name:
                return field_id
        return field_name

    def _get_operator_symbol(self, operator_name: str) -> str:
        """Gibt das Operator-Symbol für einen Operator-Namen zurück"""
        for symbol, name in self.OPERATORS.items():
            if name == operator_name:
                return symbol
        return operator_name

    def _build_query_data(self) -> Dict[str, Any]:
        """Erstellt die Query-Daten aus den Eingaben"""
        # Sammle Bedingungen
        conditions = []
        for cond in self.conditions:
            field_name = cond['field_var'].get()
            operator_name = cond['operator_var'].get()
            value = cond['value_var'].get()

            if not field_name or not operator_name:
                continue

            field_id = self._get_field_id(field_name)
            operator = self._get_operator_symbol(operator_name)

            conditions.append({
                'field': field_id,
                'operator': operator,
                'value': value
            })

        # Sammle Spalten
        columns = [field_id for field_id, var in self.column_vars.items() if var.get()]

        return {
            'name': self.name_var.get(),
            'type': 'builder',
            'builder': {
                'conditions': conditions,
                'columns': columns
            },
            'sql': None
        }

    def _preview_sql(self):
        """Zeigt eine Vorschau des generierten SQL"""
        query_data = self._build_query_data()
        sql = self._generate_sql(query_data)

        preview_window = tk.Toplevel(self.dialog)
        preview_window.title("SQL Vorschau")
        preview_window.geometry("600x300")

        text_frame = ttk.Frame(preview_window, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)

        text = tk.Text(text_frame, wrap=tk.WORD, height=10)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert('1.0', sql)
        text.config(state=tk.DISABLED)

        ttk.Button(preview_window, text="Schließen",
                  command=preview_window.destroy).pack(pady=5)

    def _generate_sql(self, query_data: Dict[str, Any]) -> str:
        """Generiert SQL aus Query-Daten"""
        builder = query_data.get('builder', {})
        conditions = builder.get('conditions', [])
        columns = builder.get('columns', ['*'])

        # SELECT
        if columns:
            if 'start_time' in columns:
                # Formatiere start_time als Datum und Zeit
                col_list = []
                for col in columns:
                    if col == 'start_time':
                        col_list.append("DATE(start_time) as date")
                        col_list.append("TIME(start_time) as time")
                    else:
                        col_list.append(col)
                sql = f"SELECT {', '.join(col_list)}"
            else:
                sql = f"SELECT {', '.join(columns)}"
        else:
            sql = "SELECT *"

        sql += " FROM contacts"

        # WHERE
        if conditions:
            where_parts = []
            for cond in conditions:
                field = cond['field']
                operator = cond['operator']
                value = cond['value']

                if operator in ('IS NULL', 'IS NOT NULL'):
                    where_parts.append(f"{field} {operator}")
                elif operator == 'LIKE' or operator == 'NOT LIKE':
                    where_parts.append(f"{field} {operator} '%{value}%'")
                else:
                    # Escape single quotes
                    value_escaped = value.replace("'", "''")
                    where_parts.append(f"{field} {operator} '{value_escaped}'")

            if where_parts:
                sql += " WHERE " + " AND ".join(where_parts)

        sql += " ORDER BY start_time DESC"

        return sql

    def _save_query(self):
        """Speichert die Abfrage"""
        name = self.name_var.get().strip()

        if not name:
            messagebox.showerror("Fehler", "Bitte geben Sie einen Namen für die Abfrage ein.")
            return

        if not self.conditions:
            messagebox.showerror("Fehler", "Bitte fügen Sie mindestens eine Bedingung hinzu.")
            return

        query_data = self._build_query_data()

        # Wenn es eine bestehende Abfrage ist, behalte die ID
        if self.existing_query:
            query_data['id'] = self.existing_query.get('id')

        try:
            self.query_manager.save_query(query_data)
            self.result = query_data
            messagebox.showinfo("Erfolg", f"Abfrage '{name}' wurde gespeichert.")
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern:\n{str(e)}")

    def _load_existing_query(self):
        """Lädt eine bestehende Abfrage in den Dialog"""
        if not self.existing_query:
            return

        # Name setzen
        self.name_var.set(self.existing_query.get('name', ''))

        # Builder-Daten laden
        builder = self.existing_query.get('builder', {})

        # Bedingungen laden
        conditions = builder.get('conditions', [])
        # Entferne die erste leere Bedingung
        if self.conditions:
            self.conditions[0]['frame'].destroy()
            self.conditions = []

        for cond in conditions:
            self._add_condition()
            last_cond = self.conditions[-1]

            # Setze Werte
            field_id = cond.get('field', '')
            field_name = self.DB_FIELDS.get(field_id, field_id)
            last_cond['field_var'].set(field_name)

            operator = cond.get('operator', '')
            operator_name = self.OPERATORS.get(operator, operator)
            last_cond['operator_var'].set(operator_name)

            last_cond['value_var'].set(cond.get('value', ''))

        # Spalten laden
        columns = builder.get('columns', [])
        for field_id, var in self.column_vars.items():
            var.set(field_id in columns)

    def show(self) -> Optional[Dict]:
        """Zeigt den Dialog modal an und gibt das Ergebnis zurück"""
        self.dialog.wait_window()
        return self.result
