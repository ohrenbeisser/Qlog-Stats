"""
Query Manager für Qlog-Stats
Verwaltet benutzerdefinierte Abfragen
"""

import json
import os
import uuid
from typing import List, Dict, Any, Optional


class QueryManager:
    """Verwaltet benutzerdefinierte Abfragen (Laden/Speichern/Löschen)"""

    def __init__(self, config_dir: str = None):
        """
        Initialisiert den Query Manager

        Args:
            config_dir: Verzeichnis für die queries.json (None = ~/.config/qlog-stats/)
        """
        if config_dir is None:
            config_dir = os.path.expanduser('~/.config/qlog-stats')

        self.config_dir = config_dir
        self.queries_file = os.path.join(config_dir, 'queries.json')

        # Erstelle Verzeichnis falls nicht vorhanden
        os.makedirs(config_dir, exist_ok=True)

        # Initialisiere queries.json falls nicht vorhanden
        if not os.path.exists(self.queries_file):
            self._create_default_file()

    def _create_default_file(self):
        """Erstellt eine leere queries.json Datei"""
        default_data = {
            "version": "1.0",
            "queries": []
        }
        with open(self.queries_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)

    def load_queries(self) -> List[Dict[str, Any]]:
        """
        Lädt alle gespeicherten Abfragen

        Returns:
            Liste von Abfrage-Dictionaries
        """
        try:
            with open(self.queries_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('queries', [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_query(self, query: Dict[str, Any]) -> str:
        """
        Speichert eine neue Abfrage oder aktualisiert eine bestehende

        Args:
            query: Abfrage-Dictionary
                {
                    "id": "optional-uuid",  # wird generiert falls nicht vorhanden
                    "name": "Abfrage-Name",
                    "type": "builder" oder "sql",
                    "builder": {...} oder None,
                    "sql": "SELECT ..." oder None,
                    "columns": ["callsign", "date", ...]
                }

        Returns:
            ID der gespeicherten Abfrage
        """
        queries = self.load_queries()

        # Generiere ID falls nicht vorhanden
        if 'id' not in query or not query['id']:
            query['id'] = str(uuid.uuid4())

        # Prüfe ob Abfrage bereits existiert (Update)
        existing_index = None
        for i, q in enumerate(queries):
            if q.get('id') == query['id']:
                existing_index = i
                break

        if existing_index is not None:
            # Update bestehende Abfrage
            queries[existing_index] = query
        else:
            # Neue Abfrage hinzufügen
            queries.append(query)

        # Speichern
        data = {
            "version": "1.0",
            "queries": queries
        }

        with open(self.queries_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return query['id']

    def delete_query(self, query_id: str) -> bool:
        """
        Löscht eine Abfrage

        Args:
            query_id: ID der zu löschenden Abfrage

        Returns:
            True wenn erfolgreich gelöscht, False wenn nicht gefunden
        """
        queries = self.load_queries()

        # Finde und entferne Abfrage
        original_length = len(queries)
        queries = [q for q in queries if q.get('id') != query_id]

        if len(queries) == original_length:
            # Nichts wurde gelöscht
            return False

        # Speichern
        data = {
            "version": "1.0",
            "queries": queries
        }

        with open(self.queries_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True

    def get_query(self, query_id: str) -> Optional[Dict[str, Any]]:
        """
        Gibt eine spezifische Abfrage zurück

        Args:
            query_id: ID der Abfrage

        Returns:
            Abfrage-Dictionary oder None wenn nicht gefunden
        """
        queries = self.load_queries()

        for query in queries:
            if query.get('id') == query_id:
                return query

        return None

    def get_query_names(self) -> List[tuple[str, str]]:
        """
        Gibt eine Liste aller Abfrage-Namen mit IDs zurück

        Returns:
            Liste von (id, name) Tupeln
        """
        queries = self.load_queries()
        return [(q.get('id'), q.get('name', 'Unbenannt')) for q in queries]
