import logging
import json
from openai import OpenAI
from openai import APIConnectionError, RateLimitError, APIError

# Настройка логгера
logger = logging.getLogger(__name__)


class ChatGPT:
    def __init__(self, api_key: str):
        logger.debug("Инициализация ChatGPT клиента")
        if not api_key:
            logger.critical("Не предоставлен API ключ для OpenAI")
            raise ValueError("API ключ обязателен для работы ChatGPT")

        try:
            self.client = OpenAI(api_key=api_key)
            logger.info("Клиент OpenAI успешно инициализирован")
        except Exception as e:
            logger.critical(f"Ошибка инициализации OpenAI клиента: {str(e)}")
            raise

    def get_response(self, prompt: str, target: str) -> dict:
        """
                Запрос ответа на заданный промпт.

                :param prompt: Текстовый запрос для ответа
                :param target: Целевая строка
                :return: Ответ на заданный промпт
        """
        logger.debug(f"Начало обработки запроса. Промпт: {prompt[:50]}...")
        logger.debug(f"Целевые данные: {target[:100]}...")

        try:
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": target}
                ],
            }

            logger.info(f"Отправка запроса к OpenAI API (модель: {payload['model']})")

            response = self.client.chat.completions.create(
                model=payload['model'],
                messages=payload['messages']
            )

            response_content = response.choices[0].message.content
            logger.debug(f"Получен сырой ответ от API: {response_content[:200]}...")

            try:
                parsed_response = json.loads(response_content)
                logger.info("Ответ успешно распарсен")
                return parsed_response

            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON ответа: {str(e)}. Ответ: {response_content[:200]}...")
                raise Exception(f"Неверный формат ответа от ChatGPT: {str(e)}")

        except RateLimitError as e:
            logger.error(f"Превышен лимит запросов к OpenAI API: {str(e)}")
            raise Exception("Превышен лимит запросов. Пожалуйста, попробуйте позже.")

        except APIConnectionError as e:
            logger.critical(f"Ошибка подключения к OpenAI API: {str(e)}")
            raise Exception("Ошибка соединения с сервером OpenAI.")

        except APIError as e:
            logger.error(f"Ошибка OpenAI API: {str(e)}")
            raise Exception(f"Ошибка API: {str(e)}")

        except Exception as e:
            logger.critical(f"Неожиданная ошибка при запросе к ChatGPT: {str(e)}")
            raise Exception(f"Произошла непредвиденная ошибка: {str(e)}")


if __name__ == "__main__":
    import os

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Необходимо установить OPENAI_API_KEY в переменных окружения")

        chat_gpt = ChatGPT(api_key)

        # Пример промпта и данных
        test_prompt = "Проанализируйте текст и верните JSON с оценкой от 1 до 10"
        test_target = "Пример текста для анализа"

        result = chat_gpt.get_response(test_prompt, test_target)
        print("Успешный результат:", result)

    except Exception as e:
        logger.error(f"Ошибка в примере использования: {str(e)}")
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


