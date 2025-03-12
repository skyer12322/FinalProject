from django import template

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