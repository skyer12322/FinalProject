import requests
from openai import OpenAI
import json
class ChatGPT:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.OpenAI = OpenAI(api_key=self.api_key)

    def get_response(self, prompt: str, target: str):
        """
        Запрос ответа на заданный промпт.

        :param prompt: Текстовый запрос для ответа
        :param target: Целевая строка
        :return: Ответ на заданный промпт
        """
        try:
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": target}
                ],
            }
            response = self.OpenAI.chat.completions.create(
                model=payload['model'],
                messages=payload['messages']
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Ошибка при запросе: {e}")