from datetime import datetime

file = open("Log.txt", "a", encoding="utf-8")
while True:
    file.write(f"\n\nТест запущен {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

