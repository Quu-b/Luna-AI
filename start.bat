@echo off
:: Испровляем шрифт в консоли
chcp 65001 > nul

echo !!!! ПРЕДУПРЕЖДЕНИЕ: ПРОГРАММА ОЧЕНЬ ТРЕБОВАТЕЛЬНАЯ (НУЖНО 8ГБ+ VRAM) !!!!

echo Проверка наличия Ollama...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Ollama не обнаружена. Начинаю автоматическую установку...
    :: Запускаем установку через PowerShell из батника
    powershell -Command "irm https://ollama.com/install.ps1 | iex"
    echo.
    echo [!] Команда установки отправлена. 
    echo [!] После завершения установки Ollama ОБЯЗАТЕЛЬНО перезапусти этот скрипт.
    pause
    exit
)


echo Начинаем запуск сервера Ollama...
:: Проверяем, не запущен ли уже сервер
tasklist /fi "imagename eq ollama.exe" | find ":" > nul
if %errorlevel% neq 0 (
    echo [OK] Сервер Ollama уже запущен.
) else (
    start /min ollama serve
    timeout /t 5 /nobreak
)

echo Загружаем/Обновляем модель "Mistral-NEMO"...
ollama pull mistral-nemo
timeout /t 3 /nobreak
cls

echo Запуск скрипта пайтон. 
echo Версия пайтона:
python --version


:: Проверяем наличие внв
if  not exist ".venv" (
	echo [.venv] Не найден, создаю свой. . . .
	python -m venv .venv
)

:: Включаем .venv ( виртуальное окружение), проверяем наши библиотеки на их наличие
call .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
python -m pip install -r requirements.txt


timeout /t 10 /nobreak
cls
echo При вылите Ошибка API:  (status code: 502), нужно перезапустить скрипт, и подольше подождать, на моем железе это происходит быстро, но на слабых неизвестно.
timeout /t 10 /nobreak
call .venv\Scripts\activate
python main.py

:: Закрываем программу
echo.
echo Завершаем работу Ollama и скрипта...
taskkill /f /im "ollama app.exe"
taskkill /f /im "ollama.exe"

echo.
echo Redy! Все закрыто, можно отдыхать ^_^
pause

:: Очень надеюсь что скрипт работает именно так, как я задумывал. (извините за неочень хорошую громатику, у меня по русскому 3 всегда было(  ))
