"""Модуль для создания вкладок интерфейса."""

from typing import Optional

import tkinter as tk
from tkinter import ttk

import pandas as pd

from tkinter import colorchooser

from constants import CATEGORY_RULES
from blackboard.plot_manager import PlotManager


def _create_text_widget_with_scroll(parent: tk.Widget, text: str) -> tk.Text:
    """Создает текстовый виджет с полосой прокрутки.

    Args:
        parent: Родительский виджет.
        text: Текст для отображения.

    Returns:
        Настроенный текстовый виджет.
    """
    text_widget = tk.Text(parent, wrap=tk.WORD, width=80, height=20)
    scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)
    text_widget.insert(tk.END, text)
    text_widget.config(state=tk.DISABLED)

    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

    return text_widget


def _pluralize(number: int, word_forms: list) -> str:
    """Склоняет слова в зависимости от числа.

    Args:
        number: Число.
        word_forms: Список форм слова [единственная, двойная, множественная].

    Returns:
        Правильная форма слова.
    """
    if number % 10 == 1 and number % 100 != 11:
        return word_forms[0]
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return word_forms[1]
    else:
        return word_forms[2]


def create_basic_info_tab(notebook: ttk.Notebook, df: pd.DataFrame) -> ttk.Frame:
    """Создает вкладку с информацией о загруженных данных.

    Args:
        notebook: Виджет блокнота.
        df: DataFrame с данными.

    Returns:
        Фрейм вкладки.
    """
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Информация")

    categorized = categorize_parameters(df.columns)

    info_parts = [
        "ИНФОРМАЦИЯ О ДАННЫХ:\n",
        f"• Всего записей: {len(df):,}",
        f"• Количество параметров: {len(df.columns)}",
        f"• Временной диапазон: {df['timestamp'].min()} - {df['timestamp'].max()}",
        f"• Длительность записи: {df['timestamp'].max() - df['timestamp'].min()}",
    ]

    for category, params in categorized.items():
        word_form = _pluralize(len(params), ['параметр', 'параметра', 'параметров'])
        info_parts.append(f"• {category}: {len(params)} {word_form}")

    info_parts.append(f"\nЗАГРУЖЕНО: {pd.Timestamp.now()}")

    info_text = "\n".join(info_parts)
    _create_text_widget_with_scroll(frame, info_text)

    return frame


def create_statics_tab(notebook: ttk.Notebook, df: pd.DataFrame) -> ttk.Frame:
    """Создает вкладку со статистикой параметров.

    Args:
        notebook: Виджет блокнота.
        df: DataFrame с данными.

    Returns:
        Фрейм вкладки.
    """
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Статистика")

    columns = ("Параметр", "Мин", "Макс", "Среднее", "Разброс", "Не-NaN")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            stats = [
                column,
                f"{df[column].min():.3f}",
                f"{df[column].max():.3f}",
                f"{df[column].mean():.3f}",
                f"{df[column].std():.3f}",
                f"{df[column].count()}/{len(df)}",
            ]
            tree.insert("", "end", values=stats)

    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    return frame

def create_parameter_values(notebook: ttk.Notebook, df: pd.DataFrame) -> ttk.Frame:
    """Создает вкладку с значениями контретного параметра.

    Args:
        notebook: Виджет блокнота.
        df: DataFrame с данными.

    Returns:
        Фрейм вкладки.
    """
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Данные")
    
    val_frame = ttk.Frame(frame)
    val_frame.pack(fill=tk.X, padx=10, pady=5)

    ttk.Label(val_frame, text="Параметр:").grid(row=0, column=0, padx=5, pady=5)
    var = tk.StringVar(value="timestamp")
    combobox = ttk.Combobox(val_frame, textvariable=var, state="readonly", width=55)
    combobox.set(df.columns[0])
    combobox["values"] = list(df.columns)
    combobox.grid(row=0, column=1, padx=5, pady=5)
    
    def show_values():
        tree.delete(*tree.get_children())
        
        param = var.get()

        
        subset = df[['timestamp', param]].dropna(subset=[param])
        
        for _, row in subset.iterrows():
            time_str = row['timestamp'].strftime('%H:%M:%S.%f')[:-3]
            tree.insert("", "end", values=(time_str, row[param]))

    def update_combobox(event):
        # Получаем текущее значение из поля ввода
        search_term = entry.get().lower()
        
        # Фильтруем список: оставляем только те элементы, которые содержат поисковый термин
        filtered_options = [option for option in df.columns if search_term in option.lower()]
        
        # Обновляем список значений Combobox
        combobox['values'] = filtered_options

    plot_btn = ttk.Button(val_frame, text="Выбрать параметр", command=show_values)
    plot_btn.grid(row=0, column=4, padx=5, pady=5)
    
    ttk.Label(val_frame, text="Поиск параметра:").grid(row=1, column=0, padx=5, pady=5)
    # Создаём поле ввода (Entry)
    entry = tk.Entry(val_frame, width=55)
    entry.grid(row=1, column=1, padx=10, pady=10)

    # Привязываем обработчик события
    entry.bind('<KeyRelease>', update_combobox)
    
    columns = ("Время", "Значение")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)


    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    return frame

    
def create_plots_tab(
    notebook: ttk.Notebook, df: pd.DataFrame, status_var: Optional[tk.StringVar] = None
) -> PlotManager:
    """Создает вкладку с интерактивным Plotly-графиком.

    Позволяет динамически добавлять/удалять несколько линий (параметров)
    произвольных цветов. 
    Зум/панорама и скрытие линий по клику по легенде реализованы средствами Plotly.

    Args:
        notebook: Виджет блокнота.
        df: DataFrame с данными.
        status_var: Переменная статуса.

    Returns:
        Экземпляр PlotManager для управления графиком.
    """
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Графики")
    
    canvas = tk.Canvas(frame, highlightthickness=0)
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    inner_frame = ttk.Frame(canvas)

    inner_frame.bind("<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    control_frame = ttk.Frame(inner_frame)
    control_frame.pack(fill=tk.X, padx=10, pady=5)

    # Выбор параметра для оси X
    ttk.Label(control_frame, text="Ось X:").grid(row=0, column=0, padx=5, pady=5)
    x_var = tk.StringVar(value="timestamp")
    x_combobox = ttk.Combobox(control_frame, textvariable=x_var, state="readonly")
    x_combobox["values"] = list(df.columns)
    x_combobox.grid(row=0, column=1, padx=5, pady=5)
    x_combobox.bind(
        "<<ComboboxSelected>>",
        lambda _: plot_manager.set_x(x_var.get()) if plot_manager else None,
    )

    # Выбор параметра для линии Y
    ttk.Label(control_frame, text="Ось Y:").grid(row=0, column=2, padx=5, pady=5)
    y_var = tk.StringVar(value=df.columns[0] if len(df.columns) else "")
    y_combobox = ttk.Combobox(control_frame, textvariable=y_var, state="readonly")
    y_combobox["values"] = list(df.columns)
    y_combobox.grid(row=0, column=3, padx=5, pady=5)

    # Выбор цвета линии
    color_var = tk.StringVar(value="#1f77b4")
    color_btn = ttk.Button(control_frame, text="Цвет", width=8)

    def choose_color():
        choice = colorchooser.askcolor(title="Выберите цвет линии")
        if choice and choice[1]:
            color_var.set(choice[1])
            color_btn.config(text=choice[1])

    color_btn.config(command=choose_color)
    color_btn.grid(row=0, column=4, padx=5, pady=5)

    # Добавление линии
    add_btn = ttk.Button(control_frame, text="+ Добавить линию по Y")

    def add_line():
        y = y_var.get()
        if y:
            plot_manager.add_line(y, color_var.get())
            update_list()

    add_btn.config(command=add_line)
    add_btn.grid(row=0, column=5, padx=5, pady=5)

    # Очистка всех линий
    clear_btn = ttk.Button(control_frame, text="Очистить")
    clear_btn.config(
        command=lambda: (plot_manager.clear(), update_list())
    )
    clear_btn.grid(row=0, column=6, padx=5, pady=5)
    
    # Фрейм для графика (в него встраивается браузер)
    plot_frame = ttk.Frame(inner_frame)
    plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


    # Создание менеджера графиков (браузер встраивается в plot_frame)
    plot_manager = PlotManager(plot_frame, df, status_var)

    # Начальная линия для наглядности
    default_y = df.columns[1] if len(df.columns) > 1 else (df.columns[0] if len(df.columns) else None)
    if default_y:
        plot_manager.add_line(default_y, color_var.get())
        
    # Список добавленных линий с возможностью удаления
    list_frame = ttk.Frame(inner_frame)
    list_frame.pack(fill=tk.X, padx=10, pady=2)

    def update_list():
        for widget in list_frame.winfo_children():
            widget.destroy()
        for t in plot_manager.traces:
            row = ttk.Frame(list_frame)
            row.pack(fill=tk.X, pady=1)
            swatch = tk.Label(row, text="   ", background=t["color"], relief=tk.RIDGE)
            swatch.pack(side=tk.LEFT, padx=4)
            ttk.Label(row, text=t["col"]).pack(side=tk.LEFT, padx=4)
            ttk.Button(
                row,
                text="✕",
                width=3,
                command=lambda col=t["col"]: (
                    plot_manager.remove_line(col),
                    update_list(),
                ),
            ).pack(side=tk.RIGHT)


    update_list()

    return plot_manager

def categorize_parameters(df_columns: list) -> dict:
    """Классифицирует параметры по категориям.

    Args:
        df_columns: Список имен столбцов.

    Returns:
        Словарь с категориями и параметрами.
    """
    categorized = {rule[0]: [] for rule in CATEGORY_RULES}
    categorized["Другие"] = []

    for column in df_columns:
        col_lower = column.lower()
        found_category = False
        for category, patterns in CATEGORY_RULES:
            if any(keyword in col_lower for keyword in patterns):
                categorized[category].append(column)
                found_category = True
                break

        if not found_category:
            categorized["Другие"].append(column)

    # Удаляет пустые категории
    return {k: v for k, v in categorized.items() if v}


def create_categorized_tabs(notebook: ttk.Notebook, df: pd.DataFrame) -> ttk.Notebook:
    """Создает вкладки для каждой категории параметров.

    Args:
        notebook: Виджет блокнота.
        df: DataFrame с данными.

    Returns:
        Обновленный виджет блокнота.
    """
    categorized = categorize_parameters(df.columns)
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Категории")

    info_parts = []
    total_parameters = 0

    for category, parameters in categorized.items():
        info_parts.append(f"\nКАТЕГОРИЯ: {category}")
        info_parts.append("-" * 50)

        if parameters:
            info_parts.append(f"Параметров: {len(parameters)}\n")
            for param in sorted(parameters):
                non_null = df[param].count()
                total = len(df)
                dtype = str(df[param].dtype)
                info_parts.append(f"• {param}")
                info_parts.append(f"  Тип: {dtype}, Заполнено: {non_null}/{total}\n")
            total_parameters += len(parameters)
        else:
            info_parts.append("Нет параметров в этой категории\n")

    info_text = "\n".join(info_parts)
    _create_text_widget_with_scroll(frame, info_text)

    return notebook

def create_analysis_tab(notebook: ttk.Notebook, df: pd.DataFrame) -> ttk.Notebook:
    """Создает вкладку для анализа и обработки данных.

    Args:
        notebook: Виджет блокнота.
        df: DataFrame с данными.

    Returns:
        Обновленный виджет блокнота.
    """
    categorized = categorize_parameters(df.columns)
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Анализ")
    
