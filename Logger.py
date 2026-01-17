import sqlite3
import re

def migrate_logs_to_db(text_file, db_file):
    # Подключаемся
    con = sqlite3.connect(db_file)
    cur = con.cursor()
    
    # Твоя таблица
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            role TEXT,
            message TEXT,
            emotion TEXT
        )
    """)

    # Читаем лог
    with open(text_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    data_to_insert = []
    
    # Регулярка для строки: [время] роль: [эмоция] текст
    # Эта штука разберет строку "[2026-01-14 21:26:26] assistant: [удивление] Привет!"
    pattern = r"\[(.*?)\] (.*?): (.*)"

    for line in lines:
        match = re.match(pattern, line)
        if match:
            timestamp, role, content = match.groups()
            
            # Вытаскиваем эмоцию из скобок, если она есть
            emotion_match = re.search(r"\[(.*?)\]", content)
            if emotion_match:
                emotion = emotion_match.group(1)
                # Убираем эмоцию из самого текста, чтобы в базе был чистый месседж
                message = re.sub(r"\[.*?\]", "", content).strip()
            else:
                emotion = "спокойствие" # дефолт, если нет эмоции
                message = content.strip()

            # Добавляем в список для массовой вставки
            data_to_insert.append((timestamp, role, message, emotion))

    # Заливаем всё разом (как в туториале про Монти Пайтон)
    cur.executemany("INSERT INTO chat_log (timestamp, role, message, emotion) VALUES (?, ?, ?, ?)", data_to_insert)
    
    con.commit()
    con.close()
    print(f"Готово! Перенесено записей: {len(data_to_insert)}")

# Запуск (убедись, что log.txt в той же папке)
migrate_logs_to_db("log.txt", "LMemory.db")