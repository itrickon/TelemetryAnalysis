@echo off
echo === Сборка Telemetry_analyzer ===
python -m nuitka --windows-console-mode=disable --windows-icon-from-ico=static/ping.ico --output-filename="Telemetry_analyzer.exe" --product-name="Telemetry_analyzer" --file-version=1.0.0.0 --product-version=1.0.0.0 main.py

if %errorlevel% neq 0 (
    echo.
    echo [ОШИБКА] Сборка не удалась!
    pause
    exit /b 1
)

echo.
echo === Создание ярлыка на рабочем столе ===
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $shortcut = $ws.CreateShortcut('%USERPROFILE%\Desktop\Telemetry_analyzer.lnk'); $shortcut.TargetPath = '%~dp0Telemetry_analyzer.exe'; $shortcut.WorkingDirectory = '%~dp0'; $shortcut.IconLocation = '%~dp0Telemetry_analyzer.exe,0'; $shortcut.Description = 'Telemetry Analyzer'; $shortcut.Save()"

echo.
echo === Готово! ===
pause