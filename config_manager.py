"""
Config Manager für Qlog-Stats
Verwaltet die Konfigurationsdatei (INI-Format)
"""

import configparser
import os
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
            'theme': 'default'
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
