from django.core.management.base import BaseCommand
from django.utils.text import slugify

from diary.models import Tag, Mood


class Command(BaseCommand):
    help = 'Load initial data (standard tags and moods)'

    def handle(self, *args, **options):
        # Стандартные теги
        standard_tags = [
            ('Работа', '#dc3545'),
            ('Учеба', '#007bff'),
            ('Личное', '#28a745'),
            ('Идеи', '#ffc107'),
            ('Книги', '#17a2b8'),
            ('Здоровье', '#6f42c1'),
            ('Путешествия', '#fd7e14'),
            ('Финансы', '#20c997'),
        ]

        for name, color in standard_tags:
            Tag.objects.get_or_create(
                name=name,
                defaults={'color': color, 'tag_type': 'standard', 'slug': slugify(name)}
            )

        # Стандартные настроения
        moods = [
            ('Очень плохое', '😢', 1),
            ('Плохое', '😞', 2),
            ('Нейтральное', '😐', 3),
            ('Хорошее', '🙂', 4),
            ('Отличное', '😊', 5),
        ]

        for name, emoji, level in moods:
            Mood.objects.get_or_create(
                name=name,
                defaults={'emoji': emoji, 'level': level}
            )

        self.stdout.write(self.style.SUCCESS('Successfully loaded initial data'))