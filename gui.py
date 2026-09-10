import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

import pandas as pd
import sv_ttk

from blackboard.data_loader import (
    load_telemetry_data,
    export_statistics_to_txt,
)
from blackboard.work_area import create_basic_info_tab, create_parameter_values, create_statics_tab
from blackboard.work_area import create_categorized_tabs, create_plots_tab, create_analysis_tab


class MainApplication(ttk.Frame):
    """Главное приложение для анализа телеметрии."""

    def __init__(self, parent: tk.Tk, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("Анализатор телеметрии")
        self.parent.geometry("1200x800")

        # Состояние приложения
        self.export_menu: Optional[tk.Menu] = None
        self.df: Optional[pd.DataFrame] = None
        self.plot_manager = None
        self.plots_tab = None

        self._set_icon()
        self._apply_theme()
        self._create_widgets()
        self._setup_layout()
        self._create_menu()

    def _set_icon(self):
        """Устанавливает иконку приложения."""
        try:
            icon = tk.PhotoImage(file="static/ping.png")
            self.parent.iconphoto(True, icon)
        except Exception:
            pass

    def _apply_theme(self):
        """Применяет тему оформления."""
        sv_ttk.set_theme("light")

    def _create_widgets(self):
        """Создает элементы интерфейса."""
        self.notebook = ttk.Notebook(self.parent)
        self.status_var = tk.StringVar(value="Готов к работе")
        self.status_bar = ttk.Label(self.parent, textvariable=self.status_var)

    def _setup_layout(self):
        """Располагает элементы интерфейса."""
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=4)

    def _create_menu(self):
        """Создает главное меню приложения."""
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)

        self._create_file_menu(menubar)
        self._create_export_menu(menubar)
        self._create_help_menu(menubar)

    def _create_file_menu(self, menubar: tk.Menu):
        """Создает меню 'Файл'."""
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть...", accelerator="Ctrl+O", command=self._open_file)
        self.parent.bind("<Control-o>", lambda _: self._open_file())
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self._exit_application)

    def _create_export_menu(self, menubar: tk.Menu):
        """Создает меню 'Экспорт'."""
        self.export_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Экспорт", menu=self.export_menu)
        self.export_menu.add_command(
            label="Экспорт графиков...",
            state="disabled",
            command=self._export_graphs
        )
        self.export_menu.add_command(
            label="Экспорт статистики...",
            state="disabled",
            command=self._export_statistics
        )

    def _create_help_menu(self, menubar: tk.Menu):
        """Создает меню 'Руководство'."""
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Руководство", menu=help_menu)
        help_menu.add_command(label="Пользователю", command=self._show_user_manual)
        help_menu.add_command(label="О программе", command=self._show_about)

    def _create_tabs(self):
        """Создает вкладки с данными телеметрии.

        Вкладка с графиком (Plotly) создается один раз и сохраняется между
        открытием файлов, чтобы не пересоздавать встроенный браузер.
        Остальные вкладки пересоздаются заново.
        """
        if self.plot_manager is None:
            for tab in self.notebook.tabs():
                self.notebook.forget(tab)
            self.plot_manager = create_plots_tab(self.notebook, self.df, self.status_var)
            self.plots_tab = self.notebook.tabs()[-1]
        else:
            self.plot_manager.df = self.df
            self.plot_manager.clear()
            self.plot_manager.refresh()

        # Пересоздаем все вкладки, кроме графика
        for tab in list(self.notebook.tabs()):
            if tab != self.plots_tab:
                self.notebook.forget(tab)

        create_basic_info_tab(self.notebook, self.df)
        create_statics_tab(self.notebook, self.df)
        create_categorized_tabs(self.notebook, self.df)
        create_parameter_values(self.notebook, self.df)
        create_analysis_tab(self.notebook, self.df)

        # Возвращаем вкладку графика на нужную позицию
        self.notebook.insert(4, self.plots_tab, text="Графики")

    def _open_file(self):
        """Открывает и загружает файл телеметрии."""
        file_path = filedialog.askopenfilename(
            title="Выберите файл телеметрии",
            filetypes=[("ULog files", "*.ulg"), ("All files", "*.*")],
        )
        if file_path:
            self.status_var.set(f"Загрузка файла: {file_path}...")
            self.update_idletasks()
            try:
                self.df = load_telemetry_data(file_path)
                self.status_var.set(f"Успех! Загружено: {len(self.df)} записей")
                self._enable_export_menus()
                self._create_tabs()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
                self.status_var.set("Ошибка загрузки файла")

    def _enable_export_menus(self):
        """Активирует пункты меню экспорта после загрузки данных."""
        self.export_menu.entryconfig(0, state="normal")
        self.export_menu.entryconfig(1, state="normal")

    def _export_graphs(self):
        """Экспортирует текущий график в файл."""
        default_filename = "telemetry_graph.png"
        file_path = filedialog.asksaveasfilename(
            title="Сохранить график",
            initialfile=default_filename,
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("Все файлы", "*.*"),
            ],
        )

        if file_path:
            try:
                figure = self.plot_manager.get_figure()
                lower = file_path.lower()
                if lower.endswith((".png", ".pdf", ".svg", ".jpeg", ".webp")):
                    figure.write_image(file_path, engine="kaleido")
                else:
                    figure.write_html(file_path)
                self.status_var.set(f"График сохранен как: {file_path}")
                messagebox.showinfo(
                    "Успех", f"График успешно экспортирован в:\n{file_path}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Ошибка экспорта", f"Не удалось экспортировать график:\n{str(e)}"
                )

    def _export_statistics(self):
        """Экспортирует статистику в текстовый файл."""
        default_filename = "telemetry_statistics.txt"
        file_path = filedialog.asksaveasfilename(
            title="Сохранить статистику",
            initialfile=default_filename,
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
        )

        if file_path:
            try:
                export_statistics_to_txt(self.df, file_path)
                self.status_var.set(f"Статистика экспортирована: {file_path}")
                messagebox.showinfo(
                    "Успех", f"Статистика успешно экспортирована в:\n{file_path}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Ошибка экспорта",
                    f"Не удалось экспортировать статистику:\n{str(e)}",
                )

    def _show_user_manual(self):
        """Показывает руководство пользователя."""
        manual_text = """
Руководство пользователя

Загрузка данных:
• Откройте меню Файл → Открыть (Ctrl+O)
• Выберите ULog файл с телеметрией
• Данные автоматически загрузятся и проанализируются

Просмотр статистики:
• Вкладка "Статистика" показывает детальную информацию по каждому параметру
• Включает минимальные/максимальные значения, среднее, стандартное отклонение
• Отображает количество заполненных значений

Построение графиков:
• Перейдите на вкладку "Графики"
• Выберите параметры для осей X и Y из выпадающих списков
• Нажмите "Построить график"
• График автоматически построится с сеткой и подписями осей

Экспорт данных:
• Экспорт статистики - Сохраняет текстовый файл с полной статистикой
• Экспорт графиков - Сохраняет графики в формате PNG/PDF

ПРИМЕЧАНИЕ:
• Если ещё не был построен ни один график,
  то при экспорте будет построен базовый график timestamp | timestamp
"""
        messagebox.showinfo("Руководство пользователя", manual_text, icon="question")

    def _show_about(self):
        """Показывает информацию о программе."""
        about_text = """
Анализатор телеметрии
Версия 0.3.7

Разработано для анализа и визуализации
данных телеметрии uav.

https://github.com/itrickon/telemetry_analysis_tt
"""
        messagebox.showinfo("О программе", about_text)

    def _exit_application(self):
        """Запрашивает подтверждение и выходит из приложения."""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            if self.plot_manager is not None:
                self.plot_manager.shutdown()
            self.parent.quit()