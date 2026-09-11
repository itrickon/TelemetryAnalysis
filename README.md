# ___Log analysis ULG___

Desktop-приложение для анализа и визуализации данных телеметрии.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Version](https://img.shields.io/badge/Version-0.2_Pre--Alpha-orange)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)

## Возможности

- **Визуализация данных** - Построение графиков любых параметров телеметрии
- **Статистический анализ** - Детальная статистика по всем параметрам
- **Категоризация** - Автоматическая группировка параметров по категориям
- **Экспорт данных** - Сохранение графиков и статистики в файлы
- **Современный интерфейс** - Интуитивно понятный GUI с светлой темой

## Технологии

- **Python 3.8+** - Основной язык программирования
- **Tkinter** - Графический интерфейс
- **Pandas** - Обработка и анализ данных
- **Plotly** - Интерактивные графики (зум, панорама, динамические линии)
- **pywebview** - Встраивание графиков в окно приложения
- **Plotly** - Интерактивные графики (зум, панорама, динамические линии)
- **pywebview** - Встраивание графиков в окно приложения
- **SV-TTK** - Современные стили для Tkinter

## Установка

### Требования
- Python 3.8 или новее
- pip (менеджер пакетов Python)

## Установка из исходного кода


### Клонирование репозитория
```
git clone https://github.com/itrickon/telemetry_analysis_tt.git
cd telemetry_analysis_tt
```

### Установка зависимостей
`pip install -r requirements.txt`

> Примечание: на Linux для работы встроенных графиков требуется системный
> WebKit2GTK, например: `sudo apt install webkit2gtk-4.1-dev`

### Для компиляции exe файла
python -m nuitka --windows-console-mode=disable --windows-icon-from-ico=static/ping.ico --output-filename="Telemetry_analyzer.exe" --product-name="telem" --file-version=1.0.0.0 --product-version=1.0.0.0 main.py


`pip install -r requirements.txt`

> Примечание: на Linux для работы встроенных графиков требуется системный
> WebKit2GTK, например: `sudo apt install webkit2gtk-4.1-dev`

### Запуск приложения
`python main.py`

### Сообщение об ошибках
Нашли ошибку? [Создайте issue](https://github.com/itrickon/telemetry_analysis_tt/issues) с подробным описанием.
