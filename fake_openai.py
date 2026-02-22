class FakeOpenAI:
    def __init__(self, llm):
        self.chat = self.Chat(llm)

    class Chat:
        def __init__(self, llm):
            self.completions = self.Completions(llm)

        class Completions:
            def __init__(self, llm):
                self.llm = llm

            def create(self, messages, **kwargs):
                # Вызываем локальную лламу
                # Важно: используем метод create_chat_completion
                response = self.llm.create_chat_completion(
                    messages=messages,
                    temperature=kwargs.get('temperature', 0.7),
                    max_tokens=kwargs.get('max_tokens', 500)
                )
                
                # Создаем структуру, которую можно читать через точку (response.choices[0]...)
                class AttrDict:
                    def __init__(self, d):
                        for key, value in d.items():
                            if isinstance(value, dict):
                                value = AttrDict(value)
                            elif isinstance(value, list):
                                value = [AttrDict(i) if isinstance(i, dict) else i for i in value]
                            setattr(self, key, value)

                return AttrDict(response)