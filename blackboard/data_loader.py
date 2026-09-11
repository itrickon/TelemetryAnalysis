"""Модуль для загрузки и экспорта данных телеметрии."""

from pathlib import Path
from typing import Union

import pandas as pd
import pyulog


def load_telemetry_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """Загружает и обрабатывает ULG файл.

    Args:
        file_path: Путь к ULG файлу.

    Returns:
        DataFrame с загруженными данными.

    Raises:
        Exception: Если не удалось загрузить файл.
    """
    ulog = pyulog.ULog(file_path)
    dfs = []

    for data in ulog.data_list:
        topic = data.name
        df_topic = pd.DataFrame(data.data)

        rename = {}
        for col in df_topic.columns:
            if col != 'timestamp':
                rename[col] = f'{topic}.{col}'
        df_topic.rename(columns=rename, inplace=True)

        num_cols = [c for c in df_topic.columns
                    if c != 'timestamp'
                    and pd.api.types.is_numeric_dtype(df_topic[c])]
        numeric_cols = ['timestamp'] + num_cols
        df_topic = df_topic[numeric_cols]

        dfs.append(df_topic)

    combined = pd.concat(dfs, axis=1)
    combined = combined.loc[:, ~combined.columns.duplicated()]
    combined['timestamp'] = pd.to_datetime(combined['timestamp'], unit='us', errors='coerce')
    combined = combined.sort_values('timestamp').reset_index(drop=True)
    combined = combined.dropna(axis=1, how='all')

    return combined


def export_statistics_to_txt(df: pd.DataFrame, filename: Union[str, Path]) -> bool:
    """Экспортирует статистику параметров в текстовый файл.

    Args:
        df: DataFrame с данными телеметрии.
        filename: Путь для сохранения файла.

    Returns:
        True если экспорт успешен, иначе False.
    """
    try:
        numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        max_param_length = max(len(str(col)) for col in df.columns)
        separator_length = max_param_length + 52 + str(len(df)).__len__()

        with open(filename, "w", encoding="utf-8") as f:
            f.write("СТАТИСТИКА ПАРАМЕТРОВ ТЕЛЕМЕТРИИ\n")
            f.write("=" * 32 + "\n")
            f.write(f"Всего записей: {len(df):,}\n")
            f.write(f"Анализируемых параметров: {len(numeric_columns)}\n")
            f.write("=" * separator_length + "\n\n")

            header = f"{'Параметр':<{max_param_length}} {'Мин':<10} {'Макс':<10} {'Среднее':<10} {'Разброс':<10} {'Заполнено':<12}\n"
            f.write(header)
            f.write("-" * separator_length + "\n")

            for column in df.columns:
                if pd.api.types.is_numeric_dtype(df[column]):
                    stats_line = (
                        f"{column:<{max_param_length}} "
                        f"{df[column].min():<10.3f} "
                        f"{df[column].max():<10.3f} "
                        f"{df[column].mean():<10.3f} "
                        f"{df[column].std():<10.3f} "
                        f"{df[column].count()}/{len(df):<12}\n"
                    )
                    f.write(stats_line)

            f.write("\n" + "=" * 50 + "\n")
            f.write(f"Файл сгенерирован: {pd.Timestamp.now()}\n")

        return True

    except Exception as e:  # pylint: disable=W0718
        print(f"Ошибка экспорта статистики: {e}")
        return False


def export_plot_as_png(df: pd.DataFrame, plot_params: list,
    status_var
) -> Union[object, None]:
    """Создает объект Plotly-Figure для экспорта.

    Args:
        df: DataFrame с данными телеметрии.
        plot_params: Список с выбранными параметрами [x_var, y_var].
        status_var: Переменная для обновления статуса.

    Returns:
        Объект plotly.graph_objects.Figure или None при ошибке.
    """
    try:
        import plotly.graph_objects as go

        x_var = plot_params[0]
        y_var = plot_params[1]

        if not x_var or not y_var:
            status_var.set("Ошибка: не выбраны оси для графика")
            return None

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df[x_var], y=df[y_var], mode="lines"))
        fig.update_layout(title=f"{x_var} | {y_var}", template="plotly_white")

        return fig

    except Exception as e:
        status_var.set(f"Ошибка сохранения: {str(e)}")
        return None
