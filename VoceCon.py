import sounddevice as sd
import numpy as np
import time


# Настройки
FS = 16000          
BLOCK_SIZE = 1024    
SILENCE_LIMIT = 1.5  
THRESHOLD = 0.04    
muted = False  # Глобальная переменная для отключения микрофона

def listen(stt_model):
    if muted: return None
    
    # Если в MAIN.py stt_model не передана (None), ничего не делаем
    if stt_model is None:
        return input("Ввод (модель STT не загружена): ")

    print("\n[Слушаю...]", end="", flush=True)
    
    audio_data = []
    is_speaking = False
    silence_start = None
    
    with sd.InputStream(samplerate=FS, channels=1, dtype='float32', blocksize=BLOCK_SIZE) as stream:
        while True:
            chunk, _ = stream.read(BLOCK_SIZE)
            audio_data.append(chunk)
            
            volume = np.sqrt(np.mean(chunk**2))
            
            if volume > THRESHOLD:
                if not is_speaking:
                    is_speaking = True
                silence_start = None
            else:
                if is_speaking:
                    if silence_start is None:
                        silence_start = time.time()
                    if time.time() - silence_start > SILENCE_LIMIT:
                        break
                else:
                    if len(audio_data) > 50: 
                        audio_data.pop(0)

    print(" -> Распознаю...")
    full_audio = np.concatenate(audio_data, axis=0)
    
    # Используем модель, пришедшую из MAIN.py
    segments, _ = stt_model.transcribe(
        full_audio.flatten(), 
        beam_size=5, 
        language="ru", 
        vad_filter=True
    )
    
    text = "".join([s.text for s in segments]).strip()
    return text if text else None