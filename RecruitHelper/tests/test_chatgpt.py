"""
Модуль с тестами для функционала ChatGPT.
"""
from unittest.mock import Mock, patch
import pytest
from RecruitHelper.chatgpt import ChatGPT

def test_get_response_success():
    """
    Тест на успешный ответ ChatGPT
    """
    with patch('RecruitHelper.chatgpt.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='{"rating": 5, "tags": ["a"]}'))]
        mock_client.chat.completions.create.return_value = mock_response

        gpt = ChatGPT(api_key='test')
        result = gpt.get_response('prompt', 'target')
        assert result == {"rating": 5, "tags": ["a"]}

def test_get_response_exception():
    """
    Тест на неудачный ответ ChatGPT
    """
    with patch('RecruitHelper.chatgpt.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("fail")
        gpt = ChatGPT(api_key='test')
        with pytest.raises(Exception) as e:
            gpt.get_response('prompt', 'target')
        assert "Ошибка при запросе: fail" in str(e.value)
