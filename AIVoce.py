import sounddevice as sd
import torch
import ssl

ssl._create_default_https_context = ssl._create_unverified_context ## Это нужно что бы программа не ругалась на сертификаты.


##  ниже актеры озвучки из модели silero-tts. Я кстати сам придумал использовать классы для группировки констант! а кстати, что такое константы?
class speakers:
    AIDAR   = "aidar"  # мужской голос
    BAYA    = "baya" # женский голос, ну как я понял, но по названию не скажешь...
    KSENIYA = "kseniya" # женский голос
    XENIA   = "xenia" # женский голос
    RANDOM  = "random" # случайный спикер из доступных


## ниже виды устройств для использования, я использую cuda, т.к. у меня видеокарта от нвидиа.
class device:
    CPU    = "cpu" ## Процессор
    VULKAN = "vulkan" ## видео движок Вулкан
    OPENGL = "opengl" ## Вимдео движок Опенгл
    OPENCL = "opencl" ## Видео движок Опенкл
    CUDA   = "cuda" ## Видео ядра нвидиа


class TTS:
    ## Функция загрузки в видеопамять
    def     __init__(
            self, speaker: str = speakers.XENIA, 
            device: str        = device.CUDA, 
            samplerate: int    = 24_000
        ):
        

        self.__MODEL__, _ = torch.hub.load(
            repo_or_dir = "snakers4/silero-models", ## репозиторий с моделями
            model = "silero_tts", ## модель озвучки, хз есть ли другие
            language = "ru", ## Язык модели
            speaker = "v5_1_ru" ##есть в3, в4, в5. В5 - самая современная
        )

        self.__MODEL__.to(torch.device(device))
        
        self.__SPEAKER__ = speaker
        self.__SAMPLERATE__ = samplerate


    def say(self, text): ## Создаем удобную функцию озвучки
        #№ Генерируем аудио
        audio = self.__MODEL__.apply_tts(
            text = text,
            put_accent = True, 
            put_yo = True,
            speaker = self.__SPEAKER__,
            sample_rate = self.__SAMPLERATE__

        )
        sd.play(audio, self.__SAMPLERATE__)
      
## P.s Код частично взят и отредактирован "https://habr.com/ru/articles/864000/", у человека с ником "PlayingPlate6667"