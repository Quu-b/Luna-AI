import time
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import json
import keyboard


##Чет я устал писать комменты, тут просто настройка голосового ввода с помощью vosk.
q = queue.Queue()
muted = False
SAMPLE_RATE = 16000
MODEL_PATH = "vosk-model-ru-0.42"


model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, SAMPLE_RATE)


 ##непроверенная функция для включения и отключения голосового ввода по кнопке "home"
def toggle_mute():
    global muted
    
    if muted == False:
        muted = True
        print("Голосовой ввод отключен.")
    else:
        muted = False
        print("Голосовой ввод включен.")


keyboard.add_hotkey('home', toggle_mute)

## Ниже часть полоностью написаная ИИ, я не понял как уменьшить ввремя задержки между окончанием речи и выводом результата, так что пришлось попросить ИИ помочь.
def callback(indata, frames, time, status):
    q.put(bytes(indata))

def listen():
    with sd.RawInputStream(samplerate=16000, blocksize=4000, dtype='int16',
                           channels=1, callback=callback): # Теперь он ее увидит
        print("Слушаю...")
        last_partial = ""
        last_change_time = time.time()
        
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                if res['text']:
                    rec.Reset()
                    return res['text']
            else:
                # Магия быстрого отклика через частичные результаты
                partial_data = json.loads(rec.PartialResult())
                partial = partial_data.get('partial', '')
                
                if partial:
                    if partial != last_partial:
                        last_partial = partial
                        last_change_time = time.time()
                    
                    # Если замолчал на 0.8 сек — забираем текст и выходим
                    elif time.time() - last_change_time > 0.8:
                        final_res = last_partial
                        rec.Reset()
                        return final_res

## ТЕСТ ГОЛОСОВОГО ВВОДА                
# while True:
#     print(listen())