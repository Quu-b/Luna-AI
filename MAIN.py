from mem0 import *
from mem0.configs.base import *
from AIVoce import *
from faster_whisper import WhisperModel
from datetime import datetime
import ollama
import locale
# Установка часового пояса\языка
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

# ---- Логирование В Log.txt ---- #
fileL = open("Log.txt", "a", encoding="utf-8")
fileL.write(f"{'='*20} НОВАЯ СЕССИЯ {'='*20}\n")
fileL.flush()

## Функция логирования в файл
def log(message, role):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if message and len(message.strip()) > 0:  ##тут мы пишем в файл логи.
        fileL.write(f"[{timestamp}] {role}: {message}\n")
        fileL.flush() 



#Включение\Выключение
OnVoce = False 

if OnVoce:
    from VoceCon import *
    print("VoceChat - Включен")
    
    print("Загрузка 'Слуха' (Faster-Whisper) на CUDA...")
    
    # Инициализируем модель модель кторая прослушивает нас
    stt_model = WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")
    #"large-v3-turbo" можено поменять на "small", "medium", "large-v2" и т.д. в зависимости от мощности вашей видюхи и нужной точности. Флоат нежелаетельно менять, а куда - моя видео карта, точнее ядра ее.

    print("--- Голосовой ввод активирован ---")

else:
    
    print("VoceChat - Выключен")


# настройка Silero
print("Загрузка голосовой модели...")
luna = TTS(speaker = speakers.XENIA) ##Создаем объект озвучки Луна выбранным голосом
print("Голосовая модель загружена!")


######################## Регистрация  и Настройка нейросетей ###############################################

# конфигурация mem-zero 
config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "mistral-nemo",
            "ollama_base_url": "http://localhost:11434"
        }
    },
    "embedder": {
        "provider": "huggingface", 
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2" 
        }
    },
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "neyro_memory",
            "path": "./chroma_db"
        }
    }
}

memory = Memory.from_config(config)


print("Проверка связи с Ollama...")
try:
    # Пытаемся получить список моделей, чтобы понять, запущен ли сервер
    models_info = ollama.list() # 
    
    # Проверяем, есть ли наша модель в списке скачанных
    downloaded_models = [m.model for m in models_info.models]
    if 'mistral-nemo:latest' not in downloaded_models and 'mistral-nemo' not in downloaded_models:
        print(" Модель mistral-nemo не найдена! Начинаю скачивание...")
        ollama.pull('mistral-nemo') # 
        print(" Загрузка завершена.")
    else:
        print(" Модель готова к общению!")
except Exception as e:
    print(f" Ошибка: Ollama не запущена! Сначала запусти приложение Ollama. ({e})")
    exit()


####################################################################### Cистемный промт ########################################################################################



#системный промт, в целом можно и без его, но если вы хотите не просто ии помошника а полноценную личность, то желательно прописать как можно дитальнее
with open("system_promt.txt", "r", encoding="utf-8") as f:
    sys_prompt = f.read()

short_term_history = []




user_id = "User0" # mem-zero использует SQ-lite, по этому чтобы нейоросеть что-то забыла, достаточно сменить пользователя


########################################## соновной цикл ############################################################

while True:

    if not OnVoce:
        user_input = input("Вы: ")
    else: ## кароче, снизу мы выризаем паузы (чаще всего все нормально, но может пригодится) (.strip) и слушаем функцию из VoceCon
        user_input = listen(stt_model)
        if not user_input or len(user_input.strip()) < 2:
            continue
        print(f"(Voce) Вы: {user_input}" )




    


    if user_input.lower() in ['q', 'exit', 'выход']:
        fileL.close()
        print("LogsClose: 'можно отправлятся на покой' ")    
        break
    
    
    #лог сообщения 
    log(user_input, "user")

    # --- ПОИСК В ДОЛГОСРОЧНОЙ ПАМЯТИ ---
    # Ищем только 3 самых подходящих факта, а не всё подряд



    relevant_memories = memory.search(user_input, user_id=user_id, limit=3)

    # Вытаскиваем только текст воспоминаний
    context_str = ""
    if isinstance(relevant_memories, list):
        context_str = "\n".join([m['memory'] for m in relevant_memories if 'memory' in m])
    elif isinstance(relevant_memories, dict) and 'results' in relevant_memories:
        context_str = "\n".join([m['memory'] for m in relevant_memories['results']])

    print(f"DEBUG: Вспомнила факты: {context_str}")



    # --- ФОРМИРОВАНИЕ СИСТЕМНОГО ПРОМПТА с памятью ---
    current_date = datetime.now().strftime("%A,%d.%m.%Y %H:%M")

    mem_block = (
        f"--- СЕГОДНЯШНЯЯ ДАТА: {current_date} ---\n"
        "БЛОК ПАМЯТИ (твои скрытые знания о пользователе):\n"
        f"{context_str}\n"
        "ИСПОЛЬЗУЙ ЭТИ ФАКТЫ ТОЛЬКО ЕСЛИ ОНИ УМЕСТНЫ. НЕ ПЕРЕСКАЗЫВАЙ ИХ ДОСЛОВНО.\n"
        "-------------------------------------------\n\n"
    ) if context_str else ""


    full_messages = [
        {"role": "system", "content": f"{mem_block}These are the system instructions:\n{sys_prompt}"}
    ]

    # Добавляем последние пару фраз для связности
    full_messages.extend(short_term_history[-14:]) 
    full_messages.append({"role": "user", "content": user_input})

    try:    

        response = ollama.chat(
            model='mistral-nemo',
            messages=full_messages,
            options={
                'temperature': 0.55,
                'num_predict': 850,
                'stop': ["</s>", "<|im_end|>"]
            }
        )

        answer = response['message']['content']


        if not answer.strip():
            print("!"*10," Луна молчит","!"*10)
            continue

        print(f"\nLuna AI: {answer}")
        

        log(answer, "assistant")
        luna.say(answer)
        


        # --- СОХРАНЕНИЕ В MEM-зеро ---
        # Mem0 сама выцепит факты из вашего диалога
        current_time_str = datetime.now().strftime("%A, %d.%m.%Y %H:%M")

        extraction_prompt = (
            f"Сегодня: {current_time_str}. Извлеки ФАКТЫ о пользователе. "
            "Игнорируй приветствия и общие вопросы. "
            "Записывай только конкретику: Имя, увлечения, предпочтения, важные события. "
            "Пример: '(23.02.2026) Имя пользователя: Админ'. Не обязательно это имя "
            "Если новой важной информации нет — НИЧЕГО не пиши."
            "Когда ты запоминаешь факты, ОБЯЗАТЕЛЬНО записывай владельца этой фразы"
        )

        memory.add(
            [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": answer}
            ], 
            user_id=user_id,
            prompt=extraction_prompt
        )

        # Обновляем короткую историю
        short_term_history.append({"role": "user", "content": user_input})
        short_term_history.append({"role": "assistant", "content": answer})

    except Exception as e:
        print(f"Ошибка API: {e}")