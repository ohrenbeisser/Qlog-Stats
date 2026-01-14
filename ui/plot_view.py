"""
Plot View Module für Qlog-Stats
Verwaltet die Matplotlib-Diagramm-Anzeige
"""

import tkinter as tk
from tkinter import messagebox

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class PlotView:
    """Verwaltet die Matplotlib-Plot-Anzeige"""

    def __init__(self, parent_frame, config_manager=None):
        """
        Initialisiert die Plot View

        Args:
            parent_frame: Tkinter Frame für das Diagramm
            config_manager: Optional ConfigManager für Theme-Erkennung
        """
        self.parent_frame = parent_frame
        self.config_manager = config_manager
        self.figure = None
        self.ax = None
        self.canvas = None
        self.canvas_widget = None
        self.is_visible = True

        # Setze Matplotlib-Farben basierend auf Theme
        self._apply_theme_colors()

    def _is_dark_mode(self):
        """Prüft ob Dark Mode aktiv ist"""
        if self.config_manager:
            try:
                return self.config_manager.get_theme_mode() == 'dark'
            except:
                pass
        return False

    def _apply_theme_colors(self):
        """Passt Matplotlib-Farben an das aktuelle Theme an"""
        if not MATPLOTLIB_AVAILABLE:
            return

        # Prüfe Theme-Modus
        is_dark = self._is_dark_mode()

        if is_dark:
            # Dark Mode Farben
            matplotlib.rcParams['figure.facecolor'] = '#2b2b2b'
            matplotlib.rcParams['axes.facecolor'] = '#2b2b2b'
            matplotlib.rcParams['axes.edgecolor'] = '#555555'
            matplotlib.rcParams['axes.labelcolor'] = '#e0e0e0'
            matplotlib.rcParams['xtick.color'] = '#e0e0e0'
            matplotlib.rcParams['ytick.color'] = '#e0e0e0'
            matplotlib.rcParams['text.color'] = '#e0e0e0'
            matplotlib.rcParams['grid.color'] = '#404040'
        else:
            # Light Mode Farben
            matplotlib.rcParams['figure.facecolor'] = 'white'
            matplotlib.rcParams['axes.facecolor'] = 'white'
            matplotlib.rcParams['axes.edgecolor'] = '#cccccc'
            matplotlib.rcParams['axes.labelcolor'] = 'black'
            matplotlib.rcParams['xtick.color'] = 'black'
            matplotlib.rcParams['ytick.color'] = 'black'
            matplotlib.rcParams['text.color'] = 'black'
            matplotlib.rcParams['grid.color'] = '#e0e0e0'

    def create_canvas(self):
        """Erstellt oder erneuert das Matplotlib Canvas"""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.parent_frame.update_idletasks()
        frame_width = self.parent_frame.winfo_width()
        frame_height = self.parent_frame.winfo_height()

        width = max(frame_width - 30, 200)
        height = max(frame_height - 60, 200)

        width_inch = width / 100
        height_inch = height / 100

        if self.canvas_widget:
            self.canvas_widget.destroy()

        self.figure = Figure(figsize=(width_inch, height_inch), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.parent_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

    def update_plot(self, data, x_key, y_key, title, xlabel, ylabel, limit=20):
        """
        Aktualisiert das Diagramm mit neuen Daten

        Args:
            data: Liste von Dictionaries mit den Daten
            x_key: Key für X-Achse (Labels)
            y_key: Key für Y-Achse (Werte)
            title: Diagramm-Titel
            xlabel: Label für X-Achse
            ylabel: Label für Y-Achse
            limit: Maximale Anzahl anzuzeigender Datenpunkte
        """
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("Fehler",
                               "matplotlib ist nicht installiert.\n"
                               "Bitte installieren mit: pip install matplotlib")
            return

        if not data:
            return

        try:
            self.create_canvas()

            plot_limit = min(limit, len(data))
            labels = [str(row[x_key]) for row in data[:plot_limit]]
            values = [row[y_key] for row in data[:plot_limit]]

            # Azure-kompatible Balkenfarbe
            bar_color = '#007acc' if not self._is_dark_mode() else '#5eb3f6'
            self.ax.bar(labels, values, color=bar_color)
            self.ax.set_xlabel(xlabel, fontsize=10)
            self.ax.set_ylabel(ylabel, fontsize=10)
            self.ax.set_title(title, fontsize=11)

            self.ax.tick_params(axis='x', rotation=45, labelsize=8)
            self.ax.tick_params(axis='y', labelsize=9)
            for label in self.ax.get_xticklabels():
                label.set_ha('right')

            # tight_layout kann bei sehr kleinen Diagrammen fehlschlagen
            try:
                self.figure.tight_layout(pad=2.0)
            except ValueError:
                # Ignoriere Fehler bei zu kleinen Layouts
                pass

            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Diagramms:\n{str(e)}")

    def update_propagation_plot(self, data, title):
        """
        Erstellt ein Liniendiagramm für Propagation-Daten mit zwei Y-Achsen

        K-Index und A-Index werden auf der linken Y-Achse dargestellt,
        SFI auf der rechten Y-Achse.

        Args:
            data: Liste von Dictionaries mit Propagation-Daten
                  Format: [{'datetime': ..., 'k_index': ..., 'a_index': ..., 'sfi': ...}, ...]
            title: Diagramm-Titel
        """
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("Fehler",
                               "matplotlib ist nicht installiert.\n"
                               "Bitte installieren mit: pip install matplotlib")
            return

        if not data:
            return

        try:
            self.create_canvas()

            # Extrahiere Daten
            from datetime import datetime
            datetimes = []
            k_values = []
            a_values = []
            sfi_values = []

            for row in data:
                try:
                    # Parse datetime string (ISO-Format mit T und Z)
                    dt_str = row.get('datetime', '')
                    if dt_str:
                        # Entferne .000Z am Ende und ersetze T mit Leerzeichen
                        dt_str_cleaned = dt_str.replace('T', ' ').replace('Z', '').split('.')[0]
                        dt = datetime.strptime(dt_str_cleaned, '%Y-%m-%d %H:%M:%S')
                        datetimes.append(dt)

                        # Hole Werte (None wenn nicht vorhanden)
                        k_val = row.get('k_index')
                        a_val = row.get('a_index')
                        sfi_val = row.get('sfi')

                        k_values.append(float(k_val) if k_val is not None else None)
                        a_values.append(float(a_val) if a_val is not None else None)
                        sfi_values.append(float(sfi_val) if sfi_val is not None else None)
                except Exception as e:
                    # Debug: Zeige welche Zeilen übersprungen werden
                    print(f"Fehler beim Parsen von Propagation-Daten: {e}, Zeile: {row}")
                    continue

            if not datetimes:
                messagebox.showinfo("Keine Daten",
                                  "Für den gewählten Zeitraum sind keine Propagation-Daten vorhanden.\n\n"
                                  "Propagation-Daten (K-Index, A-Index, SFI) werden von QLog automatisch "
                                  "beim Loggen von QSOs gespeichert, falls diese verfügbar sind.")
                return

            # Linke Y-Achse (K und A Index)
            color_k = 'tab:red'
            color_a = 'tab:blue'

            self.ax.set_xlabel('Datum/Zeit', fontsize=10)
            self.ax.set_ylabel('K-Index / A-Index', color='black', fontsize=10)

            # K-Index Linie
            line1 = self.ax.plot(datetimes, k_values, color=color_k,
                                linewidth=2, marker='o', markersize=5, label='K-Index',
                                linestyle='-', markerfacecolor=color_k, markeredgewidth=0)

            # A-Index Linie
            line2 = self.ax.plot(datetimes, a_values, color=color_a,
                                linewidth=2, marker='s', markersize=5, label='A-Index',
                                linestyle='-', markerfacecolor=color_a, markeredgewidth=0)

            self.ax.tick_params(axis='y', labelcolor='black')
            self.ax.grid(True, alpha=0.3, linestyle='--')

            # Y-Achse auto-skalieren (beginne bei 0)
            self.ax.set_ylim(bottom=0)

            # Rechte Y-Achse (SFI)
            ax2 = self.ax.twinx()
            color_sfi = 'tab:green'
            ax2.set_ylabel('SFI', color=color_sfi, fontsize=10)

            # SFI Linie
            line3 = ax2.plot(datetimes, sfi_values, color=color_sfi,
                            linewidth=2, marker='^', markersize=5, label='SFI',
                            linestyle='-', markerfacecolor=color_sfi, markeredgewidth=0)

            ax2.tick_params(axis='y', labelcolor=color_sfi)

            # Y-Achse auto-skalieren (beginne bei 0)
            ax2.set_ylim(bottom=0)

            # Titel
            self.ax.set_title(title, fontsize=11)

            # Legende kombinieren
            lines = line1 + line2 + line3
            labels = [l.get_label() for l in lines]
            self.ax.legend(lines, labels, loc='upper left')

            # X-Achse formatieren
            self.figure.autofmt_xdate()

            # tight_layout
            try:
                self.figure.tight_layout(pad=2.0)
            except ValueError:
                pass

            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Propagation-Diagramms:\n{str(e)}")

    def hide(self):
        """Blendet das Diagramm aus"""
        self.is_visible = False
        if self.canvas_widget:
            self.canvas_widget.pack_forget()

    def show(self):
        """Zeigt das Diagramm wieder an"""
        self.is_visible = True
        if self.canvas_widget:
            self.canvas_widget.pack(fill=tk.BOTH, expand=True)
