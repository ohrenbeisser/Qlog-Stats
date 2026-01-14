"""
Export Handler Module für Qlog-Stats
Verwaltet die Daten-Export-Funktionalität mit Datei-Dialog
"""

from tkinter import messagebox, filedialog
import os
from datetime import datetime


class ExportHandler:
    """Verwaltet die Daten-Export-Funktionalität"""

    def __init__(self, exporter, parent=None):
        """
        Initialisiert den Export Handler

        Args:
            exporter: StatsExporter Instanz
            parent: Parent-Fenster für Dialoge
        """
        self.exporter = exporter
        self.parent = parent
        self.current_data = None
        self.current_type = None

        self.title_map = {
            'country': 'QSOs nach Ländern',
            'band': 'QSOs nach Bändern',
            'mode': 'QSOs nach Modes',
            'year': 'QSOs nach Jahren',
            'month': 'QSOs nach Monaten',
            'weekday': 'QSOs nach Wochentagen',
            'hour': 'QSOs nach Stunden',
            'day': 'QSOs nach Tagen',
            'callsign': 'QSOs nach Rufzeichen',
            'top_days': 'Top QSO-Tage',
            'flop_days': 'Flop QSO-Tage',
            'special': 'Sonderrufzeichen',
            'callsign_search': 'Rufzeichen-Suche',
            'qsl_sent': 'QSL versendet',
            'qsl_received': 'QSL erhalten',
            'qsl_requested': 'QSL angefordert',
            'qsl_queued': 'QSL zu versenden',
            'lotw_received': 'LotW erhalten',
            'eqsl_received': 'eQSL erhalten',
            'propagation': 'Propagation-Daten'
        }

    def set_current_data(self, data, stat_type):
        """
        Setzt die aktuellen Daten für Export

        Args:
            data: Liste von Dictionaries mit den Daten
            stat_type: Typ der Statistik
        """
        self.current_data = data
        self.current_type = stat_type

    def _get_default_filename(self, extension):
        """Generiert einen Standard-Dateinamen"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base = f'qlog_{self.current_type}' if self.current_type else 'qlog_export'
        return f"{base}_{timestamp}.{extension}"

    def _get_initial_dir(self):
        """Gibt das initiale Verzeichnis für den Dialog zurück"""
        if self.exporter and hasattr(self.exporter, 'export_directory'):
            return self.exporter.export_directory
        return os.path.expanduser('~/Documents')

    def export_csv(self):
        """Exportiert aktuelle Daten als CSV mit Datei-Dialog"""
        if not self.current_data:
            messagebox.showwarning("Warnung", "Keine Daten zum Exportieren vorhanden")
            return

        filepath = filedialog.asksaveasfilename(
            parent=self.parent,
            title="CSV exportieren",
            initialdir=self._get_initial_dir(),
            initialfile=self._get_default_filename('csv'),
            defaultextension=".csv",
            filetypes=[("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")]
        )

        if not filepath:
            return  # Abgebrochen

        try:
            self._write_csv(filepath)
            messagebox.showinfo("Erfolg", f"Export erfolgreich:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Export:\n{str(e)}")

    def export_txt(self):
        """Exportiert aktuelle Daten als TXT mit Datei-Dialog"""
        if not self.current_data:
            messagebox.showwarning("Warnung", "Keine Daten zum Exportieren vorhanden")
            return

        filepath = filedialog.asksaveasfilename(
            parent=self.parent,
            title="TXT exportieren",
            initialdir=self._get_initial_dir(),
            initialfile=self._get_default_filename('txt'),
            defaultextension=".txt",
            filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
        )

        if not filepath:
            return  # Abgebrochen

        try:
            title = self.title_map.get(self.current_type, 'Qlog Statistik')
            self._write_txt(filepath, title)
            messagebox.showinfo("Erfolg", f"Export erfolgreich:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Export:\n{str(e)}")

    def export_adif(self):
        """Exportiert aktuelle Daten als ADIF 3.x mit Datei-Dialog"""
        if not self.current_data:
            messagebox.showwarning("Warnung", "Keine Daten zum Exportieren vorhanden")
            return

        # Prüfe ob es QSO-Daten sind (müssen callsign haben)
        if not any('callsign' in row for row in self.current_data):
            messagebox.showwarning("Warnung",
                "ADIF-Export ist nur für QSO-Daten verfügbar.\n"
                "Statistik-Daten (z.B. Länder-Zählung) können nicht als ADIF exportiert werden.")
            return

        filepath = filedialog.asksaveasfilename(
            parent=self.parent,
            title="ADIF exportieren",
            initialdir=self._get_initial_dir(),
            initialfile=self._get_default_filename('adi'),
            defaultextension=".adi",
            filetypes=[("ADIF-Dateien", "*.adi"), ("ADIF-Dateien", "*.adif"), ("Alle Dateien", "*.*")]
        )

        if not filepath:
            return  # Abgebrochen

        try:
            self._write_adif(filepath)
            messagebox.showinfo("Erfolg", f"ADIF-Export erfolgreich:\n{filepath}\n\n"
                               f"{len(self.current_data)} QSOs exportiert.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim ADIF-Export:\n{str(e)}")

    def _write_csv(self, filepath):
        """Schreibt CSV-Datei"""
        import csv
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if self.current_data:
                writer = csv.DictWriter(f, fieldnames=self.current_data[0].keys())
                writer.writeheader()
                writer.writerows(self.current_data)

    def _write_txt(self, filepath, title):
        """Schreibt formatierte TXT-Datei"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"{title}\n")
            f.write(f"{'=' * len(title)}\n")
            f.write(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write(f"Anzahl Einträge: {len(self.current_data)}\n\n")

            if self.current_data:
                keys = list(self.current_data[0].keys())
                col_widths = {key: max(len(str(key)), 5) for key in keys}

                # Spaltenbreiten berechnen
                for row in self.current_data:
                    for key in keys:
                        val = str(row.get(key, ''))
                        col_widths[key] = max(col_widths[key], len(val))

                # Header
                header = ' | '.join(str(key).ljust(col_widths[key]) for key in keys)
                f.write(header + '\n')
                f.write('-' * len(header) + '\n')

                # Daten
                for row in self.current_data:
                    line = ' | '.join(str(row.get(key, '')).ljust(col_widths[key]) for key in keys)
                    f.write(line + '\n')

    def _write_adif(self, filepath):
        """Schreibt ADIF 3.x Datei"""
        # ADIF Feld-Mapping (DB-Feld -> ADIF-Feld)
        adif_field_map = {
            'callsign': 'CALL',
            'start_time': 'QSO_DATE_OFF',  # Wird speziell behandelt
            'date': 'QSO_DATE',
            'time': 'TIME_ON',
            'band': 'BAND',
            'mode': 'MODE',
            'freq': 'FREQ',
            'rst_sent': 'RST_SENT',
            'rst_rcvd': 'RST_RCVD',
            'name': 'NAME',
            'qth': 'QTH',
            'gridsquare': 'GRIDSQUARE',
            'country': 'COUNTRY',
            'dxcc': 'DXCC',
            'cont': 'CONT',
            'cqz': 'CQZ',
            'ituz': 'ITUZ',
            'state': 'STATE',
            'county': 'CNTY',
            'iota': 'IOTA',
            'sota_ref': 'SOTA_REF',
            'pota_ref': 'POTA_REF',
            'wwff_ref': 'WWFF_REF',
            'tx_pwr': 'TX_PWR',
            'comment': 'COMMENT',
            'notes': 'NOTES',
            'qsl_via': 'QSL_VIA',
            'my_gridsquare': 'MY_GRIDSQUARE',
            'operator': 'OPERATOR',
            'station_callsign': 'STATION_CALLSIGN',
            'qsl_sdate': 'QSLSDATE',
            'qsl_rdate': 'QSLRDATE',
            'lotw_qslrdate': 'LOTW_QSLRDATE',
            'eqsl_qslrdate': 'EQSL_QSLRDATE',
            'k_index': 'K_INDEX',
            'a_index': 'A_INDEX',
            'sfi': 'SFI'
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            # ADIF Header
            f.write("ADIF Export from Qlog-Stats\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"QSO Count: {len(self.current_data)}\n")
            f.write("<ADIF_VER:5>3.1.4\n")
            f.write("<PROGRAMID:10>Qlog-Stats\n")
            f.write("<PROGRAMVERSION:3>3.0\n")
            f.write("<EOH>\n\n")

            # QSO Records
            for qso in self.current_data:
                record = []

                for db_field, value in qso.items():
                    if value is None or value == '':
                        continue

                    adif_field = adif_field_map.get(db_field, db_field.upper())
                    str_value = str(value)

                    # Spezialbehandlung für Datum/Zeit
                    if db_field == 'date' or db_field == 'qso_date':
                        # Format: YYYYMMDD
                        str_value = str_value.replace('-', '')[:8]
                        adif_field = 'QSO_DATE'
                    elif db_field == 'time':
                        # Format: HHMM oder HHMMSS
                        str_value = str_value.replace(':', '')[:6]
                        adif_field = 'TIME_ON'
                    elif db_field == 'start_time' and 'date' not in qso:
                        # Extrahiere Datum und Zeit aus start_time
                        if ' ' in str_value:
                            date_part, time_part = str_value.split(' ', 1)
                            record.append(f"<QSO_DATE:{len(date_part.replace('-', ''))}>{date_part.replace('-', '')}")
                            time_clean = time_part.replace(':', '')[:6]
                            record.append(f"<TIME_ON:{len(time_clean)}>{time_clean}")
                        continue
                    elif db_field in ('qsl_sdate', 'qsl_rdate', 'lotw_qslrdate', 'eqsl_qslrdate', 'qsl_date'):
                        # QSL-Datumsfelder
                        str_value = str_value.replace('-', '')[:8]

                    # Frequenz: In MHz mit Punkt
                    if db_field == 'freq' and str_value:
                        try:
                            freq_mhz = float(str_value)
                            if freq_mhz > 1000:  # Wahrscheinlich in Hz oder kHz
                                freq_mhz = freq_mhz / 1000000
                            str_value = f"{freq_mhz:.6f}"
                        except ValueError:
                            pass

                    record.append(f"<{adif_field}:{len(str_value)}>{str_value}")

                if record:
                    f.write(' '.join(record) + ' <EOR>\n')
