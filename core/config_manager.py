"""
Config Manager für Qlog-Stats
Verwaltet die Konfigurationsdatei (INI-Format)
"""

import configparser
import os
import json
from pathlib import Path


class ConfigManager:
    """Verwaltet die Konfigurationsdatei für Qlog-Stats"""

    def __init__(self, config_file='config.ini'):
        """
        Initialisiert den ConfigManager

        Args:
            config_file: Pfad zur Config-Datei (Standard: config.ini)
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        """Lädt die Konfiguration aus der Datei"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self._create_default_config()

    def _create_default_config(self):
        """Erstellt eine Standard-Konfigurationsdatei"""
        self.config['Database'] = {
            'path': os.path.expanduser('~/.local/share/hamradio/QLog/qlog.db')
        }

        self.config['Export'] = {
            'default_format': 'csv',
            'export_directory': os.path.expanduser('~/Documents/Qlog-Stats-Export')
        }

        self.config['GUI'] = {
            'window_width': '1200',
            'window_height': '800',
            'theme': 'azure',
            'theme_mode': 'light'
        }

        # Standard-Spalten für Detail-Tabellen
        from ui.table_columns import DEFAULT_COLUMNS
        self.config['TableColumns'] = {
            'detail_columns': json.dumps(DEFAULT_COLUMNS)
        }

        self.save_config()

    def save_config(self):
        """Speichert die Konfiguration in die Datei"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)

    def get_db_path(self):
        """
        Gibt den Pfad zur Qlog-Datenbank zurück

        Returns:
            str: Pfad zur Datenbank
        """
        return self.config.get('Database', 'path', fallback='')

    def set_db_path(self, path):
        """
        Setzt den Pfad zur Qlog-Datenbank

        Args:
            path: Neuer Pfad zur Datenbank
        """
        if 'Database' not in self.config:
            self.config['Database'] = {}
        self.config['Database']['path'] = path
        self.save_config()

    def get_export_directory(self):
        """Gibt das Standard-Export-Verzeichnis zurück"""
        return self.config.get('Export', 'export_directory',
                              fallback=os.path.expanduser('~/Documents/Qlog-Stats-Export'))

    def get_window_size(self):
        """Gibt die Fenstergröße zurück"""
        width = self.config.getint('GUI', 'window_width', fallback=1200)
        height = self.config.getint('GUI', 'window_height', fallback=800)
        return width, height

    def set_window_size(self, width, height):
        """Speichert die Fenstergröße"""
        if 'GUI' not in self.config:
            self.config['GUI'] = {}
        self.config['GUI']['window_width'] = str(width)
        self.config['GUI']['window_height'] = str(height)
        self.save_config()

    def get_detail_columns(self):
        """
        Gibt die konfigurierten Spalten für Detail-Tabellen zurück

        Returns:
            list: Liste von Spalten-IDs
        """
        from ui.table_columns import DEFAULT_COLUMNS

        # Hole JSON-String aus Config
        columns_json = self.config.get('TableColumns', 'detail_columns',
                                      fallback=json.dumps(DEFAULT_COLUMNS))

        try:
            columns = json.loads(columns_json)
            # Sicherstellen dass callsign immer an erster Stelle ist
            if 'callsign' in columns:
                columns.remove('callsign')
            columns.insert(0, 'callsign')
            return columns
        except json.JSONDecodeError:
            # Fallback auf Standard-Spalten bei Parse-Fehler
            return DEFAULT_COLUMNS.copy()

    def set_detail_columns(self, columns):
        """
        Speichert die Spalten für Detail-Tabellen

        Args:
            columns: Liste von Spalten-IDs
        """
        # Sicherstellen dass callsign immer an erster Stelle ist
        columns_copy = columns.copy() if isinstance(columns, list) else list(columns)
        if 'callsign' in columns_copy:
            columns_copy.remove('callsign')
        columns_copy.insert(0, 'callsign')

        if 'TableColumns' not in self.config:
            self.config['TableColumns'] = {}

        self.config['TableColumns']['detail_columns'] = json.dumps(columns_copy)
        self.save_config()

    def get_theme(self):
        """
        Gibt das ausgewählte Theme zurück

        Returns:
            str: Theme-Name ('azure' oder 'default')
        """
        return self.config.get('GUI', 'theme', fallback='azure')

    def get_theme_mode(self):
        """
        Gibt den Theme-Modus zurück

        Returns:
            str: Theme-Modus ('light' oder 'dark')
        """
        return self.config.get('GUI', 'theme_mode', fallback='light')

    def set_theme(self, theme, theme_mode='light'):
        """
        Setzt das Theme und den Theme-Modus

        Args:
            theme: Theme-Name ('azure' oder 'default')
            theme_mode: Theme-Modus ('light' oder 'dark')
        """
        if 'GUI' not in self.config:
            self.config['GUI'] = {}
        self.config['GUI']['theme'] = theme
        self.config['GUI']['theme_mode'] = theme_mode
        self.save_config()
