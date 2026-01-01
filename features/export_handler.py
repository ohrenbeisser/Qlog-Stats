"""
Export Handler Module für Qlog-Stats
Verwaltet die Daten-Export-Funktionalität
"""

from tkinter import messagebox


class ExportHandler:
    """Verwaltet die Daten-Export-Funktionalität"""

    def __init__(self, exporter):
        """
        Initialisiert den Export Handler

        Args:
            exporter: StatsExporter Instanz
        """
        self.exporter = exporter
        self.current_data = None
        self.current_type = None

        self.title_map = {
            'country': 'QSOs nach Ländern',
            'band': 'QSOs nach Bändern',
            'mode': 'QSOs nach Modes',
            'year': 'QSOs nach Jahren',
            'special': 'Sonderrufzeichen'
        }

    def set_current_data(self, data, stat_type):
        """
        Setzt die aktuellen Daten für Export

        Args:
            data: Liste von Dictionaries mit den Daten
            stat_type: Typ der Statistik (country, band, mode, year, special)
        """
        self.current_data = data
        self.current_type = stat_type

    def export_csv(self):
        """Exportiert aktuelle Daten als CSV"""
        if not self.current_data:
            messagebox.showwarning("Warnung", "Keine Daten zum Exportieren vorhanden")
            return

        try:
            filepath = self.exporter.export_to_csv(
                self.current_data,
                f'qsos_by_{self.current_type}'
            )
            messagebox.showinfo("Erfolg", f"Export erfolgreich:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Export:\n{str(e)}")

    def export_txt(self):
        """Exportiert aktuelle Daten als TXT"""
        if not self.current_data:
            messagebox.showwarning("Warnung", "Keine Daten zum Exportieren vorhanden")
            return

        try:
            title = self.title_map.get(self.current_type, 'Qlog Statistik')

            filepath = self.exporter.export_to_txt(
                self.current_data,
                f'qsos_by_{self.current_type}',
                title
            )
            messagebox.showinfo("Erfolg", f"Export erfolgreich:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Export:\n{str(e)}")
