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

    def __init__(self, parent_frame):
        """
        Initialisiert die Plot View

        Args:
            parent_frame: Tkinter Frame für das Diagramm
        """
        self.parent_frame = parent_frame
        self.figure = None
        self.ax = None
        self.canvas = None
        self.canvas_widget = None
        self.is_visible = True

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

            self.ax.bar(labels, values, color='steelblue')
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
