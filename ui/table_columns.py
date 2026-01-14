"""
Table Columns Configuration für Qlog-Stats
Definiert alle verfügbaren Spalten für Detail-Tabellen
"""

# Alle verfügbaren Spalten aus der Qlog-Datenbank
# Diese werden im Einstellungs-Dialog zur Auswahl angeboten
AVAILABLE_COLUMNS = {
    'callsign': {
        'label': 'Rufzeichen',
        'db_field': 'callsign',
        'required': True,  # Muss immer an erster Stelle sein (für QRZ-Integration)
        'format': 'text'
    },
    'start_time': {
        'label': 'Start-Zeit (UTC)',
        'db_field': 'start_time',
        'required': False,
        'format': 'datetime'
    },
    'date': {
        'label': 'Datum',
        'db_field': 'DATE(start_time)',
        'alias': 'date',
        'required': False,
        'format': 'date'
    },
    'time': {
        'label': 'Zeit',
        'db_field': 'TIME(start_time)',
        'alias': 'time',
        'required': False,
        'format': 'time'
    },
    'band': {
        'label': 'Band',
        'db_field': 'band',
        'required': False,
        'format': 'text'
    },
    'mode': {
        'label': 'Mode',
        'db_field': 'mode',
        'required': False,
        'format': 'text'
    },
    'country': {
        'label': 'Land',
        'db_field': 'country',
        'required': False,
        'format': 'text'
    },
    'dxcc': {
        'label': 'DXCC',
        'db_field': 'dxcc',
        'required': False,
        'format': 'number'
    },
    'cont': {
        'label': 'Kontinent',
        'db_field': 'cont',
        'required': False,
        'format': 'text'
    },
    'rst_sent': {
        'label': 'RST gesendet',
        'db_field': 'rst_sent',
        'required': False,
        'format': 'text'
    },
    'rst_rcvd': {
        'label': 'RST empfangen',
        'db_field': 'rst_rcvd',
        'required': False,
        'format': 'text'
    },
    'name': {
        'label': 'Name',
        'db_field': 'name',
        'required': False,
        'format': 'text'
    },
    'qth': {
        'label': 'QTH',
        'db_field': 'qth',
        'required': False,
        'format': 'text'
    },
    'gridsquare': {
        'label': 'Locator',
        'db_field': 'gridsquare',
        'required': False,
        'format': 'text'
    },
    'freq': {
        'label': 'Frequenz',
        'db_field': 'freq',
        'required': False,
        'format': 'number'
    },
    'tx_pwr': {
        'label': 'TX Power',
        'db_field': 'tx_pwr',
        'required': False,
        'format': 'number'
    },
    'my_gridsquare': {
        'label': 'Eigener Locator',
        'db_field': 'my_gridsquare',
        'required': False,
        'format': 'text'
    },
    'distance': {
        'label': 'Entfernung',
        'db_field': 'distance',
        'required': False,
        'format': 'number'
    },
    'comment': {
        'label': 'Kommentar',
        'db_field': 'comment',
        'required': False,
        'format': 'text'
    },
    'notes': {
        'label': 'Notizen',
        'db_field': 'notes',
        'required': False,
        'format': 'text'
    },
    'qsl_via': {
        'label': 'QSL via',
        'db_field': 'qsl_via',
        'required': False,
        'format': 'text'
    },
    'iota': {
        'label': 'IOTA',
        'db_field': 'iota',
        'required': False,
        'format': 'text'
    },
    'sota_ref': {
        'label': 'SOTA Ref',
        'db_field': 'sota_ref',
        'required': False,
        'format': 'text'
    },
    'pota_ref': {
        'label': 'POTA Ref',
        'db_field': 'pota_ref',
        'required': False,
        'format': 'text'
    },
    'wwff_ref': {
        'label': 'WWFF Ref',
        'db_field': 'wwff_ref',
        'required': False,
        'format': 'text'
    },
    'cqz': {
        'label': 'CQ Zone',
        'db_field': 'cqz',
        'required': False,
        'format': 'number'
    },
    'ituz': {
        'label': 'ITU Zone',
        'db_field': 'ituz',
        'required': False,
        'format': 'number'
    },
    'state': {
        'label': 'State',
        'db_field': 'state',
        'required': False,
        'format': 'text'
    },
    'county': {
        'label': 'County',
        'db_field': 'county',
        'required': False,
        'format': 'text'
    },
    'age': {
        'label': 'Alter',
        'db_field': 'age',
        'required': False,
        'format': 'number'
    },
    'operator': {
        'label': 'Operator',
        'db_field': 'operator',
        'required': False,
        'format': 'text'
    },
    'station_callsign': {
        'label': 'Station-Rufzeichen',
        'db_field': 'station_callsign',
        'required': False,
        'format': 'text'
    }
}

# Spezielle Spalte für QSL-Tabellen
QSL_DATE_COLUMN = {
    'qsl_date': {
        'label': 'QSL Datum',
        'db_field': 'qsl_date',  # wird je nach Kontext angepasst (qsl_sdate, qsl_rdate, etc.)
        'required': False,
        'format': 'date'
    }
}

# Standard-Spalten (Vorgabe beim ersten Start)
DEFAULT_COLUMNS = [
    'callsign',
    'date',
    'time',
    'band',
    'mode',
    'country'
]

def get_column_label(column_id):
    """
    Gibt das deutsche Label für eine Spalten-ID zurück

    Args:
        column_id: ID der Spalte (z.B. 'callsign')

    Returns:
        str: Deutsches Label oder die ID selbst wenn nicht gefunden
    """
    if column_id in AVAILABLE_COLUMNS:
        return AVAILABLE_COLUMNS[column_id]['label']
    elif column_id in QSL_DATE_COLUMN:
        return QSL_DATE_COLUMN[column_id]['label']
    return column_id.capitalize()

def get_db_field(column_id):
    """
    Gibt das Datenbank-Feld für eine Spalten-ID zurück

    Args:
        column_id: ID der Spalte

    Returns:
        str: Datenbank-Feldname (ggf. mit SQL-Funktion)
    """
    if column_id in AVAILABLE_COLUMNS:
        return AVAILABLE_COLUMNS[column_id]['db_field']
    elif column_id in QSL_DATE_COLUMN:
        return QSL_DATE_COLUMN[column_id]['db_field']
    return column_id

def build_select_clause(columns, qsl_date_field=None):
    """
    Baut die SELECT-Klausel für eine SQL-Query

    Args:
        columns: Liste von Spalten-IDs
        qsl_date_field: Optionales QSL-Datumsfeld (z.B. 'qsl_sdate')

    Returns:
        str: SELECT-Klausel (z.B. "callsign, DATE(start_time) as date, ...")
    """
    select_parts = []

    for col_id in columns:
        if col_id == 'qsl_date' and qsl_date_field:
            # Spezialbehandlung für QSL-Datum
            select_parts.append(f"{qsl_date_field} as qsl_date")
        elif col_id in AVAILABLE_COLUMNS:
            col_info = AVAILABLE_COLUMNS[col_id]
            db_field = col_info['db_field']

            # Wenn ein Alias definiert ist, verwende ihn
            if 'alias' in col_info:
                select_parts.append(f"{db_field} as {col_info['alias']}")
            else:
                select_parts.append(db_field)

    return ', '.join(select_parts)
