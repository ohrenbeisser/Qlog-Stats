"""
Datenbank-Modul für Qlog-Stats
Stellt nur lesenden Zugriff auf die Qlog-Datenbank bereit
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional


class QlogDatabase:
    """Nur-Lese-Zugriff auf die Qlog-Datenbank"""

    def __init__(self, db_path: str):
        """
        Initialisiert die Datenbankverbindung

        Args:
            db_path: Pfad zur Qlog-Datenbank

        Raises:
            FileNotFoundError: Wenn die Datenbank nicht existiert
        """
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Datenbank nicht gefunden: {db_path}")

        self.db_path = db_path
        self.connection = None

    def connect(self):
        """Stellt Verbindung zur Datenbank her (nur lesend)"""
        if self.connection is None:
            self.connection = sqlite3.connect(f'file:{self.db_path}?mode=ro', uri=True)
            self.connection.row_factory = sqlite3.Row

    def disconnect(self):
        """Schließt die Datenbankverbindung"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Führt eine SELECT-Query aus

        Args:
            query: SQL-Query (nur SELECT)
            params: Parameter für die Query

        Returns:
            Liste von Ergebnissen als Dictionaries

        Raises:
            ValueError: Wenn die Query keine SELECT-Query ist
        """
        if not query.strip().upper().startswith('SELECT'):
            raise ValueError("Nur SELECT-Queries sind erlaubt!")

        self.connect()
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        return results

    def _add_standard_filters(self, query: str, params: list,
                              start_date: Optional[str] = None,
                              end_date: Optional[str] = None,
                              band: Optional[str] = None,
                              mode: Optional[str] = None,
                              country: Optional[str] = None,
                              use_date_function: bool = False) -> tuple:
        """
        Fügt Standard-Filter zu einer Query hinzu (Helper-Methode)

        Args:
            query: Basis-SQL-Query
            params: Parameter-Liste
            start_date: Start-Datum (YYYY-MM-DD) optional
            end_date: End-Datum (YYYY-MM-DD) optional
            band: Band-Filter optional
            mode: Mode-Filter optional
            country: Land-Filter optional
            use_date_function: True = DATE(start_time), False = start_time

        Returns:
            Tuple von (query, params)
        """
        date_field = "DATE(start_time)" if use_date_function else "start_time"

        if start_date:
            query += f" AND {date_field} >= ?"
            params.append(start_date)
        if end_date:
            if use_date_function:
                query += f" AND {date_field} <= ?"
                params.append(end_date)
            else:
                query += f" AND {date_field} <= ?"
                params.append(end_date + ' 23:59:59')
        if band:
            query += " AND band = ?"
            params.append(band)
        if mode:
            query += " AND mode = ?"
            params.append(mode)
        if country:
            query += " AND country = ?"
            params.append(country)

        return query, params

    def get_total_qsos(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                       band: Optional[str] = None, mode: Optional[str] = None,
                       country: Optional[str] = None) -> int:
        """
        Gibt die Gesamtanzahl der QSOs zurück

        Args:
            start_date: Start-Datum (YYYY-MM-DD) optional
            end_date: End-Datum (YYYY-MM-DD) optional
            band: Band-Filter optional
            mode: Mode-Filter optional
            country: Land-Filter optional

        Returns:
            Anzahl der QSOs
        """
        query = "SELECT COUNT(*) as count FROM contacts WHERE 1=1"
        params = []
        query, params = self._add_standard_filters(query, params, start_date, end_date, band, mode, country)
        result = self.execute_query(query, tuple(params))
        return result[0]['count'] if result else 0

    def get_date_range(self) -> Dict[str, str]:
        """
        Gibt den Datumsbereich der QSOs zurück

        Returns:
            Dictionary mit min_date und max_date
        """
        query = """
            SELECT
                DATE(MIN(start_time)) as min_date,
                DATE(MAX(start_time)) as max_date
            FROM contacts
            WHERE start_time IS NOT NULL
        """
        result = self.execute_query(query)
        if result and result[0]['min_date']:
            return {
                'min_date': result[0]['min_date'],
                'max_date': result[0]['max_date']
            }
        return {'min_date': '', 'max_date': ''}

    def get_qsos_by_country(self, limit: Optional[int] = None,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None,
                           band: Optional[str] = None,
                           mode: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Gibt QSOs gruppiert nach Land zurück

        Args:
            limit: Maximale Anzahl der Ergebnisse (None = alle)
            start_date: Start-Datum (YYYY-MM-DD) optional
            end_date: End-Datum (YYYY-MM-DD) optional
            band: Band-Filter optional
            mode: Mode-Filter optional

        Returns:
            Liste mit Ländern und QSO-Anzahl
        """
        query = "SELECT country, COUNT(*) as count FROM contacts WHERE country IS NOT NULL AND country != ''"
        params = []
        query, params = self._add_standard_filters(query, params, start_date, end_date, band, mode)
        query += " GROUP BY country ORDER BY count DESC"
        if limit:
            query += f" LIMIT {limit}"
        return self.execute_query(query, tuple(params))

    def get_qsos_by_band(self, start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        mode: Optional[str] = None,
                        country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Gibt QSOs gruppiert nach Band zurück

        Args:
            start_date: Start-Datum (YYYY-MM-DD) optional
            end_date: End-Datum (YYYY-MM-DD) optional
            mode: Mode-Filter optional
            country: Land-Filter optional

        Returns:
            Liste mit Bändern und QSO-Anzahl
        """
        query = "SELECT band, COUNT(*) as count FROM contacts WHERE band IS NOT NULL AND band != ''"
        params = []
        query, params = self._add_standard_filters(query, params, start_date, end_date, mode=mode, country=country)
        query += " GROUP BY band ORDER BY count DESC"
        return self.execute_query(query, tuple(params))

    def get_qsos_by_mode(self, start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        band: Optional[str] = None,
                        country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Gibt QSOs gruppiert nach Mode zurück

        Args:
            start_date: Start-Datum (YYYY-MM-DD) optional
            end_date: End-Datum (YYYY-MM-DD) optional
            band: Band-Filter optional
            country: Land-Filter optional

        Returns:
            Liste mit Modes und QSO-Anzahl
        """
        query = "SELECT mode, COUNT(*) as count FROM contacts WHERE mode IS NOT NULL AND mode != ''"
        params = []
        query, params = self._add_standard_filters(query, params, start_date, end_date, band, country=country)
        query += " GROUP BY mode ORDER BY count DESC"
        return self.execute_query(query, tuple(params))

    def get_qsos_by_year(self, start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        band: Optional[str] = None,
                        mode: Optional[str] = None,
                        country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Gibt QSOs gruppiert nach Jahr zurück

        Args:
            start_date: Start-Datum (YYYY-MM-DD) optional
            end_date: End-Datum (YYYY-MM-DD) optional
            band: Band-Filter optional
            mode: Mode-Filter optional
            country: Land-Filter optional

        Returns:
            Liste mit Jahren und QSO-Anzahl
        """
        query = "SELECT strftime('%Y', start_time) as year, COUNT(*) as count FROM contacts WHERE start_time IS NOT NULL"
        params = []
        query, params = self._add_standard_filters(query, params, start_date, end_date, band, mode, country)
        query += " GROUP BY year ORDER BY year DESC"
        return self.execute_query(query, tuple(params))

    def get_qsos_by_month(self, start_date: Optional[str] = None,
                          end_date: Optional[str] = None,
                          band: Optional[str] = None,
                          mode: Optional[str] = None,
                          country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Gibt QSOs gruppiert nach Monat zurück

        Args:
            start_date: Start-Datum (YYYY-MM-DD) optional
            end_date: End-Datum (YYYY-MM-DD) optional
            band: Band-Filter optional
            mode: Mode-Filter optional
            country: Land-Filter optional

        Returns:
            Liste mit Monaten und QSO-Anzahl
        """
        query = "SELECT strftime('%Y-%m', start_time) as month, COUNT(*) as count FROM contacts WHERE start_time IS NOT NULL"
        params = []
        query, params = self._add_standard_filters(query, params, start_date, end_date, band, mode, country)
        query += " GROUP BY month ORDER BY month DESC"
        return self.execute_query(query, tuple(params))

    def get_qsos_by_weekday(self, start_date: Optional[str] = None,
                            end_date: Optional[str] = None,
                            band: Optional[str] = None,
                            mode: Optional[str] = None,
                            country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Gibt QSOs gruppiert nach Wochentag zurück

        Args:
            start_date: Start-Datum (YYYY-MM-DD) optional
            end_date: End-Datum (YYYY-MM-DD) optional
            band: Band-Filter optional
            mode: Mode-Filter optional
            country: Land-Filter optional

        Returns:
            Liste mit Wochentagen und QSO-Anzahl
        """
        query = """SELECT CASE CAST(strftime('%w', start_time) AS INTEGER)
            WHEN 0 THEN 'Sonntag' WHEN 1 THEN 'Montag' WHEN 2 THEN 'Dienstag'
            WHEN 3 THEN 'Mittwoch' WHEN 4 THEN 'Donnerstag' WHEN 5 THEN 'Freitag'
            WHEN 6 THEN 'Samstag' END as weekday, COUNT(*) as count,
            CAST(strftime('%w', start_time) AS INTEGER) as day_num
            FROM contacts WHERE start_time IS NOT NULL"""
        params = []
        query, params = self._add_standard_filters(query, params, start_date, end_date, band, mode, country)
        query += " GROUP BY day_num ORDER BY day_num"
        return self.execute_query(query, tuple(params))

    def get_qsos_by_hour(self, start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         band: Optional[str] = None,
                         mode: Optional[str] = None,
                         country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Gibt QSOs gruppiert nach Stunde (0-23) zurück

        Args:
            start_date: Start-Datum (YYYY-MM-DD) optional
            end_date: End-Datum (YYYY-MM-DD) optional
            band: Band-Filter optional
            mode: Mode-Filter optional
            country: Land-Filter optional

        Returns:
            Liste mit Stunden und QSO-Anzahl
        """
        query = "SELECT CAST(strftime('%H', start_time) AS INTEGER) as hour, COUNT(*) as count FROM contacts WHERE start_time IS NOT NULL"
        params = []
        query, params = self._add_standard_filters(query, params, start_date, end_date, band, mode, country)
        query += " GROUP BY hour ORDER BY hour"
        return self.execute_query(query, tuple(params))

    def get_qsos_by_day(self, start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        band: Optional[str] = None,
                        mode: Optional[str] = None,
                        country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Gibt QSOs gruppiert nach Tag (des Monats) zurück

        Args:
            start_date: Start-Datum (YYYY-MM-DD) optional
            end_date: End-Datum (YYYY-MM-DD) optional
            band: Band-Filter optional
            mode: Mode-Filter optional
            country: Land-Filter optional

        Returns:
            Liste mit Tagen und QSO-Anzahl
        """
        query = "SELECT CAST(strftime('%d', start_time) AS INTEGER) as day, COUNT(*) as count FROM contacts WHERE start_time IS NOT NULL"
        params = []
        query, params = self._add_standard_filters(query, params, start_date, end_date, band, mode, country)
        query += " GROUP BY day ORDER BY day"
        return self.execute_query(query, tuple(params))

    def get_top_qso_days(self, start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         band: Optional[str] = None,
                         mode: Optional[str] = None,
                         country: Optional[str] = None,
                         limit: Optional[int] = 250) -> List[Dict[str, Any]]:
        """
        Gibt die Tage mit den meisten QSOs zurück

        Args:
            start_date: Start-Datum (YYYY-MM-DD) optional
            end_date: End-Datum (YYYY-MM-DD) optional
            band: Band-Filter optional
            mode: Mode-Filter optional
            country: Land-Filter optional
            limit: Maximale Anzahl der Ergebnisse (Standard: 250)

        Returns:
            Liste mit Tagen (Datum) und QSO-Anzahl
        """
        query = "SELECT DATE(start_time) as date, COUNT(*) as count FROM contacts WHERE start_time IS NOT NULL"
        params = []
        query, params = self._add_standard_filters(query, params, start_date, end_date, band, mode, country)
        query += " GROUP BY date ORDER BY count DESC"
        if limit:
            query += f" LIMIT {limit}"
        return self.execute_query(query, tuple(params))

    def get_flop_qso_days(self, start_date: Optional[str] = None,
                          end_date: Optional[str] = None,
                          band: Optional[str] = None,
                          mode: Optional[str] = None,
                          country: Optional[str] = None,
                          limit: Optional[int] = 250) -> List[Dict[str, Any]]:
        """
        Gibt die Tage mit den wenigsten QSOs zurück

        Args:
            start_date: Start-Datum (YYYY-MM-DD) optional
            end_date: End-Datum (YYYY-MM-DD) optional
            band: Band-Filter optional
            mode: Mode-Filter optional
            country: Land-Filter optional
            limit: Maximale Anzahl der Ergebnisse (Standard: 250)

        Returns:
            Liste mit Tagen (Datum) und QSO-Anzahl
        """
        query = "SELECT DATE(start_time) as date, COUNT(*) as count FROM contacts WHERE start_time IS NOT NULL"
        params = []
        query, params = self._add_standard_filters(query, params, start_date, end_date, band, mode, country)
        query += " GROUP BY date ORDER BY count ASC"
        if limit:
            query += f" LIMIT {limit}"
        return self.execute_query(query, tuple(params))

    def get_qsos_by_callsign(self, start_date: Optional[str] = None,
                             end_date: Optional[str] = None,
                             band: Optional[str] = None,
                             mode: Optional[str] = None,
                             country: Optional[str] = None,
                             limit: Optional[int] = 1000) -> List[Dict[str, Any]]:
        """
        Gibt QSOs gruppiert nach Rufzeichen zurück

        Args:
            start_date: Start-Datum (YYYY-MM-DD) optional
            end_date: End-Datum (YYYY-MM-DD) optional
            band: Band-Filter optional
            mode: Mode-Filter optional
            country: Land-Filter optional
            limit: Maximale Anzahl der Ergebnisse (Standard: 1000)

        Returns:
            Liste mit Rufzeichen und QSO-Anzahl
        """
        query = "SELECT callsign, COUNT(*) as count FROM contacts WHERE callsign IS NOT NULL AND callsign != ''"
        params = []
        query, params = self._add_standard_filters(query, params, start_date, end_date, band, mode, country)
        query += " GROUP BY callsign ORDER BY count DESC"
        if limit:
            query += f" LIMIT {limit}"
        return self.execute_query(query, tuple(params))

    def get_special_callsigns(self, start_date: Optional[str] = None,
                              end_date: Optional[str] = None,
                              band: Optional[str] = None,
                              mode: Optional[str] = None,
                              country: Optional[str] = None,
                              columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Gibt alle QSOs mit Sonderrufzeichen zurück (weltweit)

        Sonderrufzeichen-Kriterien:
        - Mehrere aufeinanderfolgende Ziffern im Rufzeichen (z.B. DL2025W, 9A100IARU)
        - Suffix länger als 3 Buchstaben (z.B. 3Z0XMAS, DA0IARU)

        Normale Rufzeichen-Struktur: [Präfix: 1-2 Buchstaben] + [EINE Ziffer] + [Suffix: 2-3 Buchstaben]
        Beispiele normal: DL6LG, K3AB, 9A2L
        Beispiele Sonder: DL75DARC (75=2 Ziffern), DA0IARU (IARU=4 Buchstaben)

        Args:
            start_date: Start-Datum (YYYY-MM-DD) optional
            end_date: End-Datum (YYYY-MM-DD) optional
            band: Band-Filter optional
            mode: Mode-Filter optional
            country: Land-Filter optional

        Returns:
            Liste mit QSOs von Sonderrufzeichen
        """
        import re
        from ui.table_columns import build_select_clause

        # Bestimme die SELECT-Spalten
        if columns:
            select_clause = build_select_clause(columns)
        else:
            # Fallback auf Standard-Spalten
            select_clause = "callsign, DATE(start_time) as date, TIME(start_time) as time, band, mode, country, dxcc"

        # Hole alle QSOs (ohne Portable-Stationen)
        query = f"""
            SELECT
                {select_clause}
            FROM contacts
            WHERE callsign IS NOT NULL
            AND callsign NOT LIKE '%/%'
        """
        params = []

        if start_date:
            query += " AND start_time >= ?"
            params.append(start_date)
        if end_date:
            query += " AND start_time <= ?"
            params.append(end_date + ' 23:59:59')
        if band:
            query += " AND band = ?"
            params.append(band)
        if mode:
            query += " AND mode = ?"
            params.append(mode)
        if country:
            query += " AND country = ?"
            params.append(country)

        query += " ORDER BY start_time DESC"

        all_qsos = self.execute_query(query, tuple(params))

        # Bekannte Präfixe, die mit einer Ziffer enden (ITU-Standard)
        # Diese müssen von der "mehrere Ziffern"-Regel ausgenommen werden
        KNOWN_DIGIT_PREFIXES = {
            # Format: Präfix mit Ziffer, z.B. 'A6' für UAE
            'A4', 'A6', 'A7', 'A9',  # Oman, UAE, Qatar, Bahrain
            'C3',                     # Andorra
            'E7',                     # Bosnien-Herzegowina
            'S5',                     # Slowenien
            'T7',                     # San Marino
            'V5',                     # Namibia
            'Z3',                     # Nordmazedonien
            'Z6',                     # Kosovo
            '2E', '2M', '2W',        # UK (Foundation, Intermediate)
            '3Z',                     # Polen (special)
            '4J', '4K', '4L', '4X', '4Z',  # Azerbaijan, Georgia, Israel
            '5B', '5C', '5H', '5N', '5R', '5T', '5U', '5V', '5W', '5X', '5Z',
            '6O', '6V', '6W', '6Y',
            '7P', '7Q', '7X',
            '8P', '8Q', '8R', '8S',
            '9A', '9H', '9J', '9K', '9L', '9M', '9N', '9Q', '9U', '9V', '9X', '9Y'
        }

        # Filtere Sonderrufzeichen in Python
        special_qsos = []

        for qso in all_qsos:
            call = qso['callsign']

            # Analysiere Rufzeichen-Struktur
            # Finde Suffix (nur Buchstaben am Ende)
            suffix_match = re.search(r'([A-Z]+)$', call)
            if not suffix_match:
                continue

            suffix = suffix_match.group(1)
            prefix_and_number = call[:-len(suffix)]

            # Kriterium 1: Suffix länger als 3 Buchstaben -> Sonderrufzeichen
            if len(suffix) > 3:
                special_qsos.append(qso)
                continue

            # Kriterium 2: Mehrere aufeinanderfolgende Ziffern im Distrikt-Bereich
            # Finde alle Ziffern-Sequenzen
            digit_sequences = re.findall(r'\d+', prefix_and_number)

            if not digit_sequences:
                continue

            # Finde die LETZTE (rechteste) Ziffern-Sequenz -> Das ist die Distrikt-Nummer
            last_digit_seq = digit_sequences[-1]
            last_digit_pos = prefix_and_number.rfind(last_digit_seq)
            prefix = prefix_and_number[:last_digit_pos]

            # Prüfe die Länge der Distrikt-Nummer
            district_len = len(last_digit_seq)

            if district_len == 1:
                # Normale 1-Ziffer Distrikt-Nummer -> Normal
                continue
            elif district_len == 2:
                # 2 Ziffern: Könnte Präfix+Distrikt sein (z.B. A6+5) oder echtes Sonder (DL+75)
                # Prüfe ob [Präfix + erste Ziffer der Sequenz] ein bekanntes Präfix ist
                potential_prefix = prefix + last_digit_seq[0]

                if potential_prefix in KNOWN_DIGIT_PREFIXES:
                    # z.B. A65RW: prefix="A", last_digit_seq="65", potential_prefix="A6"
                    # A6 ist bekanntes Präfix -> Normal (A6 + 5 + RW)
                    continue
                else:
                    # z.B. DL75DARC: prefix="DL", last_digit_seq="75", potential_prefix="DL7"
                    # DL7 ist KEIN bekanntes Präfix -> Sonderrufzeichen (DL + 75 + DARC)
                    special_qsos.append(qso)
            else:
                # 3+ Ziffern -> definitiv Sonderrufzeichen (z.B. DL2025W, 9A100IARU)
                special_qsos.append(qso)

        return special_qsos

    def get_all_bands(self) -> List[str]:
        """
        Gibt eine Liste aller verfügbaren Bänder zurück

        Returns:
            Liste von Band-Namen (sortiert nach Häufigkeit)
        """
        query = """
            SELECT DISTINCT band
            FROM contacts
            WHERE band IS NOT NULL AND band != ''
            ORDER BY band
        """
        results = self.execute_query(query)
        return [row['band'] for row in results]

    def get_all_modes(self) -> List[str]:
        """
        Gibt eine Liste aller verfügbaren Modes zurück

        Returns:
            Liste von Mode-Namen (sortiert alphabetisch)
        """
        query = """
            SELECT DISTINCT mode
            FROM contacts
            WHERE mode IS NOT NULL AND mode != ''
            ORDER BY mode
        """
        results = self.execute_query(query)
        return [row['mode'] for row in results]

    def get_all_countries(self) -> List[str]:
        """
        Gibt eine Liste aller verfügbaren Länder zurück

        Returns:
            Liste von Ländernamen (sortiert alphabetisch)
        """
        query = """
            SELECT DISTINCT country
            FROM contacts
            WHERE country IS NOT NULL AND country != ''
            ORDER BY country
        """
        results = self.execute_query(query)
        return [row['country'] for row in results]

    def search_callsigns(self, search_term: str,
                        search_mode: str = 'partial',
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        band: Optional[str] = None,
                        mode: Optional[str] = None,
                        country: Optional[str] = None,
                        columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Sucht nach Rufzeichen (beginnend oder Teilstring)

        Args:
            search_term: Suchbegriff
            search_mode: 'beginning' für Suche ab Beginn, 'partial' für Teilstring-Suche
            start_date: Startdatum (YYYY-MM-DD) für Filter
            end_date: Enddatum (YYYY-MM-DD) für Filter
            band: Band-Filter
            mode: Mode-Filter
            country: Land-Filter

        Returns:
            Liste von QSO-Dictionaries mit Details (callsign, date, time, band, mode, country)
        """
        self.connect()
        from ui.table_columns import build_select_clause

        select_clause = build_select_clause(columns) if columns else \
            "callsign, DATE(start_time) as date, TIME(start_time) as time, band, mode, country"

        query = f"SELECT {select_clause} FROM contacts WHERE 1=1"
        params = []

        if search_term:
            pattern = f"{search_term}%" if search_mode == 'beginning' else f"%{search_term}%"
            query += " AND UPPER(callsign) LIKE UPPER(?)"
            params.append(pattern)

        query, params = self._add_standard_filters(query, params, start_date, end_date, band, mode, country, use_date_function=True)
        query += " ORDER BY start_time DESC"
        return self.execute_query(query, tuple(params))

    def _get_qsl_data(self, where_clause: str, qsl_date_field: Optional[str] = None,
                      start_date: Optional[str] = None, end_date: Optional[str] = None,
                      band: Optional[str] = None, mode: Optional[str] = None,
                      country: Optional[str] = None, columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Generische Helper-Methode für QSL-Abfragen

        Args:
            where_clause: WHERE-Bedingung (z.B. "qsl_sdate IS NOT NULL")
            qsl_date_field: Optionales QSL-Datumsfeld für build_select_clause
            start_date: Startdatum (YYYY-MM-DD) für Filter
            end_date: Enddatum (YYYY-MM-DD) für Filter
            band: Band-Filter
            mode: Mode-Filter
            country: Land-Filter
            columns: Optionale Spaltenliste

        Returns:
            Liste von QSO-Dictionaries
        """
        self.connect()
        from ui.table_columns import build_select_clause

        if columns:
            select_clause = build_select_clause(columns, qsl_date_field=qsl_date_field)
        else:
            base_cols = "callsign, DATE(start_time) as date, TIME(start_time) as time, band, mode, country"
            select_clause = f"{base_cols}, {qsl_date_field} as qsl_date" if qsl_date_field else base_cols

        query = f"SELECT {select_clause} FROM contacts WHERE {where_clause}"
        params = []
        query, params = self._add_standard_filters(query, params, start_date, end_date, band, mode, country, use_date_function=True)
        query += " ORDER BY start_time DESC"
        return self.execute_query(query, tuple(params))

    def get_qsl_sent(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                    band: Optional[str] = None, mode: Optional[str] = None,
                    country: Optional[str] = None, columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Gibt alle QSOs mit versendeten QSL-Karten zurück"""
        return self._get_qsl_data("qsl_sdate IS NOT NULL", "qsl_sdate", start_date, end_date, band, mode, country, columns)

    def get_qsl_received(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                        band: Optional[str] = None, mode: Optional[str] = None,
                        country: Optional[str] = None, columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Gibt alle QSOs mit erhaltenen QSL-Karten zurück"""
        return self._get_qsl_data("qsl_rdate IS NOT NULL", "qsl_rdate", start_date, end_date, band, mode, country, columns)

    def get_qsl_requested(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                         band: Optional[str] = None, mode: Optional[str] = None,
                         country: Optional[str] = None, columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Gibt alle QSOs mit angeforderten QSL-Karten zurück"""
        return self._get_qsl_data("qsl_rcvd = 'R'", None, start_date, end_date, band, mode, country, columns)

    def get_qsl_queued(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                      band: Optional[str] = None, mode: Optional[str] = None,
                      country: Optional[str] = None, columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Gibt alle QSOs mit zu versendenden QSL-Karten zurück"""
        return self._get_qsl_data("qsl_sent = 'Q'", None, start_date, end_date, band, mode, country, columns)

    def get_lotw_received(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                         band: Optional[str] = None, mode: Optional[str] = None,
                         country: Optional[str] = None, columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Gibt alle QSOs mit LotW-Bestätigungen zurück"""
        return self._get_qsl_data("lotw_qsl_rcvd = 'Y'", "lotw_qslrdate", start_date, end_date, band, mode, country, columns)

    def get_eqsl_received(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                         band: Optional[str] = None, mode: Optional[str] = None,
                         country: Optional[str] = None, columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Gibt alle QSOs mit eQSL-Bestätigungen zurück"""
        return self._get_qsl_data("eqsl_qsl_rcvd = 'Y'", "eqsl_qslrdate", start_date, end_date, band, mode, country, columns)

    def get_database_info(self) -> Dict[str, Any]:
        """
        Gibt Informationen über die Datenbank zurück

        Returns:
            Dictionary mit DB-Informationen
        """
        self.connect()
        info = {
            'path': self.db_path,
            'size': os.path.getsize(self.db_path),
            'total_qsos': self.get_total_qsos()
        }
        return info

    def get_table_columns(self) -> List[Dict[str, Any]]:
        """
        Gibt alle Spalten der contacts-Tabelle zurück

        Returns:
            Liste von Dictionaries mit Spalteninformationen
            Format: [{'cid': 0, 'name': 'id', 'type': 'INTEGER', ...}, ...]
        """
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("PRAGMA table_info(contacts)")
        columns = []
        for row in cursor.fetchall():
            columns.append({
                'cid': row[0],
                'name': row[1],
                'type': row[2],
                'notnull': row[3],
                'default': row[4],
                'pk': row[5]
            })
        return columns

    def get_propagation_data(self, start_date: Optional[str] = None,
                            end_date: Optional[str] = None,
                            band: Optional[str] = None,
                            mode: Optional[str] = None,
                            country: Optional[str] = None,
                            **kwargs) -> List[Dict[str, Any]]:
        """
        Holt Propagation-Daten (K-Index, A-Index, SFI) aus der Datenbank.
        Doppelte aufeinanderfolgende Werte werden gefiltert.

        Returns:
            Liste von Dictionaries mit Propagation-Daten
        """
        self.connect()
        query = "SELECT start_time as datetime, k_index, a_index, sfi FROM contacts WHERE (k_index IS NOT NULL OR a_index IS NOT NULL OR sfi IS NOT NULL)"
        params = []
        query, params = self._add_standard_filters(query, params, start_date, end_date, band, mode, country, use_date_function=True)
        query += " ORDER BY start_time ASC"

        results = self.execute_query(query, tuple(params))
        if not results:
            return []

        # Filtere doppelte aufeinanderfolgende Werte
        filtered_results = []
        last_values = None
        for row in results:
            current_values = (row.get('k_index'), row.get('a_index'), row.get('sfi'))
            if current_values != last_values:
                filtered_results.append(dict(row))
                last_values = current_values
        return filtered_results

    def __enter__(self):
        """Context Manager: Verbindung öffnen"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager: Verbindung schließen"""
        self.disconnect()
