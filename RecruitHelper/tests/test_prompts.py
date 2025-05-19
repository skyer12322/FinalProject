"""
Модуль с тестами для шаблонов запросов ChatGPT.
"""
import pytest
from RecruitHelper.prompts import TAGS_ASSIGN, JOB_RANKING, JOB_RANKING_CANDIDATE

def test_tags_assign_prompt_structure():
    """
    Тест структуры шаблона запроса для присвоения тегов
    """
    # Проверка наличия ключевых фраз в шаблоне
    assert "Ты опытный HR-специалист" in TAGS_ASSIGN
    assert "Общее количество тегов СТРОГО не должно превышать 10" in TAGS_ASSIGN
    assert "Формат ответа" in TAGS_ASSIGN
    assert "{\"tags\":" in TAGS_ASSIGN
    
    # Проверка наличия инструкций по категориям тегов
    assert "Сфера (IT, маркетинг, финансы и т. д.)" in TAGS_ASSIGN
    assert "Тип занятости (офис, удаленка, гибрид)" in TAGS_ASSIGN
    assert "Уровень (junior, middle, senior, lead)" in TAGS_ASSIGN
    assert "Ключевые технологии/навыки" in TAGS_ASSIGN
    assert "Условия (гибкий график, соцпакет, релокация)" in TAGS_ASSIGN

def test_job_ranking_prompt_structure():
    """
    Тест структуры шаблона запроса для ранжирования вакансии
    """
    # Проверка наличия ключевых фраз в шаблоне
    assert "Ранжируй вакансию по метрике" in JOB_RANKING
    assert "Зарплата – главный фактор" in JOB_RANKING
    assert "Позиция (должность)" in JOB_RANKING
    assert "Требуемые навыки" in JOB_RANKING
    assert "Условия работы" in JOB_RANKING
    
    # Проверка наличия формулы расчета
    assert "Рейтинг =" in JOB_RANKING
    assert "0.5" in JOB_RANKING
    assert "0.166" in JOB_RANKING
    
    # Проверка формата ответа
    assert "{\"rating\":" in JOB_RANKING
    assert "целое число от 1 до 100" in JOB_RANKING

def test_job_ranking_candidate_prompt_structure():
    """
    Тест структуры шаблона запроса для ранжирования кандидата
    """
    # Проверка наличия ключевых фраз в шаблоне
    assert "Ты — опытный HR-специалист" in JOB_RANKING_CANDIDATE
    assert "Критерии оценки" in JOB_RANKING_CANDIDATE
    assert "Соответствие опыта" in JOB_RANKING_CANDIDATE
    assert "Достижения" in JOB_RANKING_CANDIDATE
    assert "Совпадение с ценностями компании" in JOB_RANKING_CANDIDATE
    assert "Техническая экспертиза" in JOB_RANKING_CANDIDATE
    assert "Soft skills" in JOB_RANKING_CANDIDATE
    
    # Проверка формата ответа
    assert "'rank': X" in JOB_RANKING_CANDIDATE
    assert "'recommendation':" in JOB_RANKING_CANDIDATE
    
    # Проверка наличия ограничений
    assert "Не используй субъективные суждения" in JOB_RANKING_CANDIDATE
    assert "Не добавляй критерии, не указанные в вакансии" in JOB_RANKING_CANDIDATE