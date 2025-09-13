from django import template
from django.urls import resolve

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


# Новые теги для навигации
@register.simple_tag(takes_context=True)
def is_active(context, url_name):
    """
    Проверяет, является ли текущий URL активным для данного имени URL.
    Использование: {% is_active 'url_name' %}
    """
    try:
        current_url = context["request"].path
        resolved_url = resolve(current_url)

        # Проверяем совпадение имен URL
        if resolved_url.url_name == url_name:
            return "active"

        # Для некоторых URL может потребоваться проверка по namespace
        if hasattr(resolved_url, "app_name") and resolved_url.app_name == "diary":
            if resolved_url.url_name == url_name:
                return "active"

    finally:
        print("pass")

    return ""


@register.simple_tag(takes_context=True)
def is_active_pattern(context, pattern):
    """
    Проверяет, соответствует ли текущий URL заданному паттерну.
    Использование: {% is_active_pattern 'entries' %}
    """
    try:
        current_url = context["request"].path
        if pattern in current_url:
            return "active"
    finally:
        print("pass")

    return ""


@register.simple_tag(takes_context=True)
def is_active_in(context, *url_names):
    """
    Проверяет, находится ли текущий URL в списке имен.
    """
    try:
        current_url_name = resolve(context["request"].path).url_name
        if current_url_name in url_names:
            return "active"
    finally:
        print("pass")

    return ""

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)