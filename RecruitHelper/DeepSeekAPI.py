import requests

class DeepSeekAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        print(self.api_key)
        self.base_url = "https://api.deepseek.com/v1/chat/completions"

    def get_job_rankings(self, prompt: str, num_results: int = 5):
        """
        Запрос ранжировки вакансий по заданному промпту.

        :param prompt: Текстовый запрос для ранжировки вакансий
        :param num_results: Количество результатов для возврата
        :return: Список ранжированных вакансий
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            "num_results": num_results
        }
        payload = {
            "model": "deepseek-chat",  # Уточните название модели
            "messages": [
                {"role": "system", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()  # Возвращаем результаты в формате JSON
        else:
            raise Exception(f"Ошибка при запросе: {response.status_code} - {response.text}")

"""
Пример использования:

if __name__ == "__main__":
    api_key = "API_KEY"  # Укажите ваш API ключ
    deepseek = DeepSeekAPI(api_key)

    try:
        prompt = "Сам промпт"
        rankings = deepseek.get_job_rankings(prompt)
        print(rankings)
    except Exception as e:
        print(f"Произошла ошибка: {e}")

"""


