import logging
import json
from openai import OpenAI
from openai import APIConnectionError, RateLimitError, APIError
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class ChatGPT:
    """
    Класс клиента для взаимодействия с OpenAI API.
    """
    def __init__(self, api_key: str):
        """
        Инициализирует клиент ChatGPT.

        :param api_key: API ключ для доступа к OpenAI API.
        :raises ValueError: Если API ключ не предоставлен.
        """
        logger.debug("Initializing ChatGPT client")
        if not api_key:
            logger.critical("Missing OpenAI API key")
            raise ValueError("API key required for ChatGPT")

        try:
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.critical(f"OpenAI client initialization failed: {str(e)}")
            raise

    def get_response(self, prompt: str, target: str) -> dict:
        """
        Отправляет запрос к OpenAI API и возвращает обработанный ответ.

        :param prompt: Системный промпт для модели.
        :param target: Входные данные пользователя для модели.
        :return: Словарь с ответом от модели.
        :raises Exception: В случае различных ошибок API или обработки ответа.
        """
        logger.debug(f"Processing request. Prompt: {prompt[:50]}...")
        logger.debug(f"Input data: {target[:100]}...")

        try:
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": target}
                ],
            }

            logger.info(f"Sending request to OpenAI API (model: {payload['model']})")

            response = self.client.chat.completions.create(
                model=payload['model'],
                messages=payload['messages']
            )

            response_content = response.choices[0].message.content
            logger.debug(f"Received raw API response: {response_content[:200]}...")

            try:
                parsed_response = json.loads(response_content)
                logger.info("Response parsed successfully")
                return parsed_response

            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {str(e)}. Response: {response_content[:200]}...")
                raise Exception(f"Invalid ChatGPT response format: {str(e)}")

        except RateLimitError as e:
            logger.error(f"OpenAI API rate limit exceeded: {str(e)}")
            raise Exception("Rate limit exceeded. Please try again later.")

        except APIConnectionError as e:
            logger.critical(f"OpenAI API connection failed: {str(e)}")
            raise Exception("OpenAI server connection error.")

        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"API error: {str(e)}")

        except Exception as e:
            logger.critical(f"Unexpected ChatGPT error: {str(e)}")
            raise Exception(f"Ошибка при запросе: {str(e)}")
