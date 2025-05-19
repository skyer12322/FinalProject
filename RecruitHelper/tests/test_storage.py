"""
Модуль с тестами для хранилища.
"""
import pytest
from RecruitHelper.storage import local_storage

def test_local_storage_attributes():
    """
    Тест атрибутов локального хранилища
    """
    # Проверка, что можно установить и получить атрибут
    local_storage.test_attr = "test_value"
    assert local_storage.test_attr == "test_value"
    
    # Проверка, что можно изменить атрибут
    local_storage.test_attr = "new_value"
    assert local_storage.test_attr == "new_value"
    
    # Проверка, что можно удалить атрибут
    delattr(local_storage, 'test_attr')
    assert not hasattr(local_storage, 'test_attr')

def test_local_storage_isolation():
    """
    Тест изоляции локального хранилища между разными экземплярами
    """
    from threading import local
    
    # Создаем новый экземпляр local
    another_storage = local()
    
    # Устанавливаем атрибуты в разных хранилищах
    local_storage.attr1 = "value1"
    another_storage.attr2 = "value2"
    
    # Проверяем, что атрибуты не пересекаются
    assert hasattr(local_storage, 'attr1')
    assert not hasattr(local_storage, 'attr2')
    assert hasattr(another_storage, 'attr2')
    assert not hasattr(another_storage, 'attr1')