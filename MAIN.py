from mem0 import *
from mem0.configs.base import *
from AIVoce import *
from faster_whisper import WhisperModel
from datetime import datetime
from llama_cpp import Llama
from fake_openai import FakeOpenAI

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

path_model = "Mistral-Nemo-Instruct-2407-GGUF\Mistral-Nemo-Instruct-2407-Q4_K_M.gguf" #сюда путь до нашей нейросети

llm = Llama(
    model_path=path_model,
    n_gpu_layers=-1,      # на сколько мы разрешаем использовать видеокарту
    n_ctx=4096,           # Контекст
    flash_attn=True,      # нейросетевой-ускоритель для виокарт примерно 40+ поколения
    chat_format="chatml", # Чтобы понимала структуру диалога
    verbose=False # логи
)

# конфигурация mem-zero 
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4o",
            "api_key": "sk-" + "1"*48,
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
memory.llm.client = FakeOpenAI(llm)



####################################################################### Cистемный промт ########################################################################################



#системный промт, в целом можно и без его, но если вы хотите не просто ии помошника а полноценную личность, то желательно прописать как можно дитальнее
with open("system_promt.txt", "r", encoding="utf-8") as f:
    sys_prompt = f.read()

short_term_history = []


########################################## соновной цикл ############################################################

while True:

    if not OnVoce:
        user_input = input("Вы: ")
    else: ## кароче, снизу мы виризаем паузы (чаще всего все нормально, но может пригодится) (.strip) и слушаем функцию из VoceCon
        user_input = listen(stt_model)
        if not user_input or len(user_input.strip()) < 2:
            continue
        print(f"(Voce) Вы: {user_input}" )



    user_id = "User3" # mem-zero использует SQ-lite, по этому чтобы нейоросеть что-то забыла, достаточно сменить пользователя
    


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
    if relevant_memories and 'results' in relevant_memories:
        context_str = "\n".join([m['memory'] for m in relevant_memories['results']])



    # --- ФОРМИРОВАНИЕ СИСТЕМНОГО ПРОМПТА с памятью ---
    # Мы подсовываем факты как "Системные знания"
    full_messages = [
        {"role": "system", "content": f"{sys_prompt}. Твои знания о пользователе:\n{context_str}"}
    ]
    # Добавляем последние пару фраз для связности
    full_messages.extend(short_term_history[-4:]) 
    full_messages.append({"role": "user", "content": user_input})

    try:    

        completion = llm.create_chat_completion(
            messages = full_messages,
            temperature = 0.65, ## Креатив нейронки
            max_tokens = 500,
            frequency_penalty = 0.6, ## Штраф за повторение одних и тех же слов
            presence_penalty = 0.6,  ## Штраф за топтание на одной теме, поощряет новые мысли
            stop=["</s>", "<|im_end|>"]
        )

        answer = completion['choices'][0]['message']['content']

        if not answer.strip():
            print("!"*10," Луна молчит","!"*10)
            continue

        print(f"\nLuna AI: {answer}")
        
        log(answer, "assistant")
        luna.say(answer)
        
        # --- СОХРАНЕНИЕ В MEM-зеро ---
        # Mem0 сама выцепит факты из вашего диалога
        memory.add([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": answer}
        ], user_id=user_id)

        # Обновляем короткую историю
        short_term_history.append({"role": "user", "content": user_input})
        short_term_history.append({"role": "assistant", "content": answer})

    except Exception as e:
        print(f"Ошибка API: {e}")