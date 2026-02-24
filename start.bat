@echo off
:: Испровляем шрифт в консоли
chcp 65001 > nul

echo !!!! ПРЕДУПРЕЖДЕНИЕ: ПРОГРАММА ОЧЕНЬ ТРЕБОВАТЕЛЬНАЯ (НУЖНО 8ГБ+ VRAM) !!!!

echo Начинаем запуск сервера OLlama. . . . .
start /min ollama serve
:: timeout /t 10 /nobreak

echo Загружаем модель "Mistral-NEMO"
ollama pull mistral-nemo
:: timeout /t 3 /nobreak
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
python -m pip install -r requirements.txt
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

:: timeout /t 5 /nobreak

call .venv\Scripts\activate
python main.py

:: Закрываем программу
echo.
echo Завершаем работу Ollama и скрипта...
taskkill /f /im ollama.exe 

echo.
echo Redy! Все закрыто, можно отдыхать ^_^
pause

:: Очень надеюсь что скрипт работает именно так, как я задумывал. (извините за неочень хорошую громатику, у меня по русскому 3 всегда было(  ))
