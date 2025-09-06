import os
import re

from colorfield.fields import ColorField
from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.text import slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from users.models import User


class Tag(models.Model):
    COLOR_PALETTE = (
        ("#6aa958", "Зеленый",),
        ("#ca1d23", "Красный",),
        ("#003d92", "Синий",),
        ("#72757a", "Серый",),
        ("#e7949e", "Розовый",),
    )

    name = models.CharField(
        max_length=30,
        unique=True,
        verbose_name='Название',
        validators=[MinLengthValidator(2, "Тег должен быть не короче 2 символов")]
    )
    color = ColorField(samples=COLOR_PALETTE, default="#e7949e")
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Владелец',
        help_text='Для стандартных тегов владелец не указан',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        blank=True,
        verbose_name='Слаг'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Entry(models.Model):
    MOOD_LEVEL = (
        (1, '😢 Очень плохое'),
        (2, '😞 Плохое'),
        (3, '😐 Нейтральное'),
        (4, '🙂 Хорошее'),
        (5, '😊 Отличное'),
    )

    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        validators=[MinLengthValidator(3, "Заголовок должен быть не короче 3 символов")]
    )
    content = MarkdownxField(verbose_name='Содержание')  # Для markdown
    content_html = models.TextField(editable=False,
                                    verbose_name='HTML содержимое')  # Для хранения сконвертированного HTML
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    date_updated = models.DateTimeField(auto_now=True, verbose_name='Обновлена')
    entry_date = models.DateField(verbose_name='Дата записи', help_text='Дата, к которой относится запись')
    mood = models.IntegerField(choices=MOOD_LEVEL, verbose_name='Уровень настроения', default=5)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Теги')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец', null=True)
    word_count = models.PositiveIntegerField(default=0, verbose_name='Количество слов')

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def save(self, *args, **kwargs):
        # Конвертация markdown в HTML (можно использовать markdown2 или другую библиотеку)
        self.content_html = markdownify(self.content)
        # Конвертация markdown в HTML
        self.content_html = markdownify(self.content)
        # Подсчет слов
        self.word_count = len(self.content.split())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.entry_date}: {self.title}"

    # @property
    # def word_count(self):
    #     """Количество слов в записи"""
    #     return len(self.content.split())

    def get_first_image(self):
        # Ищем первое изображение в HTML-содержимом
        if self.content_html:
            # Используем регулярное выражение для поиска тегов img
            img_tags = re.findall(r'<img[^>]+src="([^">]+)"', self.content_html)
            if img_tags:
                return img_tags[0]
        return None
