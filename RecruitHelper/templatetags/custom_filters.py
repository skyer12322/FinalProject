from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})


@register.filter(name='format_skills')
def format_skills(value):
    """Форматируем список навыков, убираем скобки и разделяем запятой"""
    if isinstance(value, list):
        return ', '.join(value)
    return value

@register.filter(name="is_instance")
def is_instance(obj, model_str):
    app_label = "RecruitHelper"
    model_name = model_str.lower()
    obj_type = ContentType.objects.get_for_model(obj)
    return obj_type.app_label == app_label and obj_type.model == model_name