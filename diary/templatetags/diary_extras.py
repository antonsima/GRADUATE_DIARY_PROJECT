from django import template
from diary.models import Entry

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_mood_display(value):
    # Преобразуем числовое значение настроения в текстовое представление
    for mood_value, mood_display in Entry.MOOD_LEVEL:
        if mood_value == value:
            return mood_display
    return value