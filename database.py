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
        query = """
            SELECT country, COUNT(*) as count
            FROM contacts
            WHERE country IS NOT NULL AND country != ''
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
        query = """
            SELECT band, COUNT(*) as count
            FROM contacts
            WHERE band IS NOT NULL AND band != ''
        """
        params = []

        if start_date:
            query += " AND start_time >= ?"
            params.append(start_date)
        if end_date:
            query += " AND start_time <= ?"
            params.append(end_date + ' 23:59:59')
        if mode:
            query += " AND mode = ?"
            params.append(mode)
        if country:
            query += " AND country = ?"
            params.append(country)

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
        query = """
            SELECT mode, COUNT(*) as count
            FROM contacts
            WHERE mode IS NOT NULL AND mode != ''
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
        if country:
            query += " AND country = ?"
            params.append(country)

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
        query = """
            SELECT strftime('%Y', start_time) as year, COUNT(*) as count
            FROM contacts
            WHERE start_time IS NOT NULL
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
        query = """
            SELECT strftime('%Y-%m', start_time) as month, COUNT(*) as count
            FROM contacts
            WHERE start_time IS NOT NULL
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
        query = """
            SELECT
                CASE CAST(strftime('%w', start_time) AS INTEGER)
                    WHEN 0 THEN 'Sonntag'
                    WHEN 1 THEN 'Montag'
                    WHEN 2 THEN 'Dienstag'
                    WHEN 3 THEN 'Mittwoch'
                    WHEN 4 THEN 'Donnerstag'
                    WHEN 5 THEN 'Freitag'
                    WHEN 6 THEN 'Samstag'
                END as weekday,
                COUNT(*) as count,
                CAST(strftime('%w', start_time) AS INTEGER) as day_num
            FROM contacts
            WHERE start_time IS NOT NULL
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

        query += " GROUP BY day_num ORDER BY day_num"

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
        query = """
            SELECT CAST(strftime('%d', start_time) AS INTEGER) as day, COUNT(*) as count
            FROM contacts
            WHERE start_time IS NOT NULL
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
        query = """
            SELECT DATE(start_time) as date, COUNT(*) as count
            FROM contacts
            WHERE start_time IS NOT NULL
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
        query = """
            SELECT DATE(start_time) as date, COUNT(*) as count
            FROM contacts
            WHERE start_time IS NOT NULL
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
        query = """
            SELECT callsign, COUNT(*) as count
            FROM contacts
            WHERE callsign IS NOT NULL AND callsign != ''
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

        query += " GROUP BY callsign ORDER BY count DESC"

        if limit:
            query += f" LIMIT {limit}"

        return self.execute_query(query, tuple(params))

    def get_special_callsigns(self, start_date: Optional[str] = None,
                              end_date: Optional[str] = None,
                              band: Optional[str] = None,
                              mode: Optional[str] = None,
                              country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Gibt alle QSOs mit Sonderrufzeichen zurück

        Sonderrufzeichen haben:
        - Mehr als eine Zahl im Callsign
        - DR-Präfix
        - 0 als zweite Ziffer (z.B. DL0, DA0)

        Args:
            start_date: Start-Datum (YYYY-MM-DD) optional
            end_date: End-Datum (YYYY-MM-DD) optional
            band: Band-Filter optional
            mode: Mode-Filter optional
            country: Land-Filter optional

        Returns:
            Liste mit QSOs von Sonderrufzeichen
        """
        query = """
            SELECT
                callsign,
                DATE(start_time) as date,
                TIME(start_time) as time,
                band,
                mode,
                country,
                dxcc
            FROM contacts
            WHERE callsign IS NOT NULL
            AND callsign NOT LIKE '%/%'
            AND (
                (callsign LIKE 'DR%')
                OR (callsign LIKE 'DL0%' OR callsign LIKE 'DA0%' OR callsign LIKE 'DF0%'
                    OR callsign LIKE 'DK0%' OR callsign LIKE 'DO0%' OR callsign LIKE 'DB0%'
                    OR callsign LIKE 'DC0%' OR callsign LIKE 'DD0%' OR callsign LIKE 'DE0%'
                    OR callsign LIKE 'DG0%' OR callsign LIKE 'DH0%' OR callsign LIKE 'DJ0%'
                    OR callsign LIKE 'DM0%' OR callsign LIKE 'DN0%' OR callsign LIKE 'DP0%')
                OR (callsign GLOB 'D[LABFKOGCDEHJMNP][0-9][0-9]*')
                OR (callsign GLOB 'D[LABFKOGCDEHJMNP][1-9][0-9]*[0-9]*')
            )
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

        return self.execute_query(query, tuple(params))

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

    def __enter__(self):
        """Context Manager: Verbindung öffnen"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager: Verbindung schließen"""
        self.disconnect()
