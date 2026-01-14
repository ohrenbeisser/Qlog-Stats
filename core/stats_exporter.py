"""
Statistik-Export-Modul für Qlog-Stats
Exportiert Statistiken in verschiedene Formate
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Any


class StatsExporter:
    """Exportiert Statistiken in verschiedene Formate"""

    def __init__(self, export_directory: str):
        """
        Initialisiert den Exporter

        Args:
            export_directory: Verzeichnis für Exports
        """
        self.export_directory = export_directory
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        """Stellt sicher, dass das Export-Verzeichnis existiert"""
        os.makedirs(self.export_directory, exist_ok=True)

    def _generate_filename(self, base_name: str, extension: str) -> str:
        """
        Generiert einen Dateinamen mit Zeitstempel

        Args:
            base_name: Basis-Dateiname
            extension: Dateiendung (ohne Punkt)

        Returns:
            Vollständiger Dateipfad
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{base_name}_{timestamp}.{extension}"
        return os.path.join(self.export_directory, filename)

    def export_to_csv(self, data: List[Dict[str, Any]], base_name: str = 'qlog_stats') -> str:
        """
        Exportiert Daten als CSV

        Args:
            data: Liste von Dictionaries mit Daten
            base_name: Basis-Dateiname

        Returns:
            Pfad zur erstellten Datei
        """
        if not data:
            raise ValueError("Keine Daten zum Exportieren vorhanden")

        filepath = self._generate_filename(base_name, 'csv')

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        return filepath

    def export_to_txt(self, data: List[Dict[str, Any]], base_name: str = 'qlog_stats',
                      title: str = 'Qlog Statistik') -> str:
        """
        Exportiert Daten als formatierte Textdatei

        Args:
            data: Liste von Dictionaries mit Daten
            base_name: Basis-Dateiname
            title: Titel für die Textdatei

        Returns:
            Pfad zur erstellten Datei
        """
        if not data:
            raise ValueError("Keine Daten zum Exportieren vorhanden")

        filepath = self._generate_filename(base_name, 'txt')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"{title}\n")
            f.write(f"{'=' * len(title)}\n")
            f.write(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")

            if data:
                keys = list(data[0].keys())
                col_widths = {key: len(str(key)) for key in keys}

                for row in data:
                    for key in keys:
                        col_widths[key] = max(col_widths[key], len(str(row[key])))

                header = ' | '.join(str(key).ljust(col_widths[key]) for key in keys)
                f.write(header + '\n')
                f.write('-' * len(header) + '\n')

                for row in data:
                    line = ' | '.join(str(row[key]).ljust(col_widths[key]) for key in keys)
                    f.write(line + '\n')

        return filepath

    def export_country_stats(self, country_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Exportiert Länder-Statistiken in mehrere Formate

        Args:
            country_data: Länder-Daten

        Returns:
            Dictionary mit Dateipfaden für jeden Export
        """
        exports = {}
        exports['csv'] = self.export_to_csv(country_data, 'qsos_by_country')
        exports['txt'] = self.export_to_txt(country_data, 'qsos_by_country',
                                           'QSOs nach Ländern')
        return exports
