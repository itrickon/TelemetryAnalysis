"""Менеджер интерактивных графиков на базе matplotlib, встроенный в окно Tkinter.

   График отрисовывается средствами matplotlib + FigureCanvasTkAgg
"""

import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import plotly.graph_objects as go

from constants import get_unit


DEFAULT_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
]


class PlotManager:
    """Менеджер интерактивного matplotlib-графика, встроенного в Tkinter."""

    def __init__(self, parent_frame: tk.Widget, df, status_var=None):
        self.parent = parent_frame
        self.df = df
        self.status_var = status_var
        self.x_col = "timestamp"
        self.traces = []
        self._color_index = 0

        self.fig = Figure(facecolor="white")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("white")

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


        self.toolbar = NavigationToolbar2Tk(self.canvas, parent_frame)
        self.toolbar.update()

        self._legend_visible = {}

    def next_color(self) -> str:
        """Возвращает следующий цвет из палитры по кругу."""
        color = DEFAULT_COLORS[self._color_index % len(DEFAULT_COLORS)]
        self._color_index += 1
        return color

    def set_x(self, col: str):
        """Устанавливает столбец для оси X и перерисовывает график."""
        self.x_col = col
        self.refresh()

    def add_line(self, col: str, color: str = None):
        """Добавляет линию (параметр) с указанным цветом."""
        if color is None:
            color = self.next_color()
        if not any(t["col"] == col for t in self.traces):
            self.traces.append({"col": col, "color": color})
            self._legend_visible[col] = True
        self.refresh()

    def remove_line(self, col: str):
        """Удаляет линию по имени параметра."""
        self.traces = [t for t in self.traces if t["col"] != col]
        self._legend_visible.pop(col, None)
        self.refresh()

    def clear(self):
        """Удаляет все линии."""
        self.traces = []
        self._color_index = 0
        self._legend_visible.clear()
        self.refresh()

    def build_fig(self) -> go.Figure:
        """Строит объект Plotly Figure из текущих данных и линий (для экспорта)."""
        fig = go.Figure()
        x = self.df[self.x_col]

        for t in self.traces:
            col = t["col"]
            if col in self.df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=self.df[col],
                        mode="lines",
                        name=col,
                        line=dict(color=t["color"]),
                    )
                )

        xu = get_unit(self.x_col)
        x_title = f"{self.x_col} ({xu})" if xu else self.x_col
        
        fig.update_layout(
            title=f"{self.x_col} | линий: {len(self.traces)}",
            xaxis_title=x_title,
            yaxis_title="значение",
            template="plotly_white",
            legend=dict(orientation="v", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=50, r=20, t=50, b=40),
        )
        
        return fig

    def refresh(self):
        """Перерисовывает matplotlib-график с текущими данными."""
        self.ax.clear()

        x = self.df[self.x_col]
        plotted = []

        for t in self.traces:
            col = t["col"]
            if col in self.df.columns and self._legend_visible.get(col, True):
                self.ax.plot(x, self.df[col], color=t["color"], label=col, linewidth=1)
                plotted.append(col)

        xu = get_unit(self.x_col)
        x_title = f"{self.x_col} ({xu})" if xu else self.x_col

        self.ax.set_title(f"{self.x_col} | линий: {len(self.traces)}")
        self.ax.set_xlabel(x_title)
        self.ax.set_ylabel("значение")



        self.fig.tight_layout()
        self.canvas.draw()

        if self.status_var:
            visible = sum(1 for v in self._legend_visible.values() if v)
            self.status_var.set(
                f"График обновлён: {len(self.traces)} линий, видимых: {visible}"
            )

    def _on_legend_pick(self, event):
        """Обрабатывает клик по элементу легенды — переключает видимость линии."""
        leg = self.ax.get_legend()
        if leg is None:
            return
        lines = leg.get_lines()
        labels = [t.get_text() for t in leg.get_texts()]

        if event.artist not in lines:
            return

        idx = lines.index(event.artist)
        if idx >= len(labels):
            return

        col = labels[idx]
        current = self._legend_visible.get(col, True)
        self._legend_visible[col] = not current
        self.refresh()

    def get_figure(self) -> go.Figure:
        """Возвращает текущий Plotly Figure для экспорта."""
        return self.build_fig()

    def shutdown(self):
        """Очищает ресурсы matplotlib."""
        try:
            self.toolbar.destroy()
            self.canvas.get_tk_widget().destroy()
        except Exception:
            pass
