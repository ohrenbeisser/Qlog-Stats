"""
QRZ Integration Module für Qlog-Stats
Verwaltet die Integration mit QRZ.com
"""

import webbrowser


class QRZIntegration:
    """Verwaltet die Integration mit QRZ.com"""

    @staticmethod
    def open_link(event, tree_widget):
        """
        Öffnet QRZ.com für das ausgewählte Rufzeichen

        Args:
            event: Tkinter Event (wird für Callback benötigt)
            tree_widget: Treeview-Widget mit den Daten
        """
        selected = tree_widget.selection()
        if selected:
            item = tree_widget.item(selected[0])
            values = item['values']
            if values:
                callsign = values[0]
                url = f"https://www.qrz.com/db/{callsign}"
                webbrowser.open(url)

    @staticmethod
    def create_callback(tree_widget):
        """
        Erstellt einen Callback für das gegebene Treeview-Widget

        Args:
            tree_widget: Treeview-Widget

        Returns:
            Callback-Funktion
        """
        return lambda event: QRZIntegration.open_link(event, tree_widget)
