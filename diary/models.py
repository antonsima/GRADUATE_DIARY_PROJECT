import os

from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.text import slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from users.models import User


class Tag(models.Model):
    # Типы тегов: стандартные (встроенные) и пользовательские
    TAG_TYPE_CHOICES = (
        ('standard', 'Стандартный'),
        ('custom', 'Пользовательский'),
    )

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название',
        validators=[MinLengthValidator(2, "Тег должен быть не короче 2 символов")]
    )
    slug = models.SlugField(max_length=50, unique=True, verbose_name='URL-адрес')
    color = models.CharField(
        max_length=7,
        default='#6c757d',  # Bootstrap secondary color
        verbose_name='Цвет (HEX)',
        help_text='Цвет тега в формате HEX (например, #007bff)'
    )
    tag_type = models.CharField(
        max_length=10,
        choices=TAG_TYPE_CHOICES,
        default='custom',
        verbose_name='Тип тега'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Владелец',
        help_text='Для стандартных тегов владелец не указан'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['tag_type', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Mood(models.Model):
    MOOD_LEVEL = (
        (1, '😢 Очень плохое'),
        (2, '😞 Плохое'),
        (3, '😐 Нейтральное'),
        (4, '🙂 Хорошее'),
        (5, '😊 Отличное'),
    )

    name = models.CharField(max_length=100, verbose_name='Название настроения')
    emoji = models.CharField(max_length=5, verbose_name='Эмодзи')
    level = models.IntegerField(choices=MOOD_LEVEL, verbose_name='Уровень настроения')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Настроение'
        verbose_name_plural = 'Настроения'
        ordering = ['level']

    def __str__(self):
        return f"{self.emoji} {self.name}"


class Entry(models.Model):
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
    is_public = models.BooleanField(default=False, verbose_name='Публичная запись')
    mood = models.ForeignKey(
        Mood,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Настроение'
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Теги')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')

    content = MarkdownxField(verbose_name='Содержание')
    content_html = models.TextField(editable=False, verbose_name='HTML содержимое')

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-entry_date', '-date_created']
        unique_together = ['owner', 'entry_date']  # Одна запись на день для пользователя

    def save(self, *args, **kwargs):
        # Конвертация markdown в HTML (можно использовать markdown2 или другую библиотеку)
        self.content_html = markdownify(self.content)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.entry_date}: {self.title}"

    @property
    def word_count(self):
        """Количество слов в записи"""
        return len(self.content.split())

    @property
    def reading_time(self):
        """Примерное время чтения (средняя скорость 200 слов в минуту)"""
        return max(1, round(self.word_count / 200))


def attachment_path(instance, filename):
    # Файлы будут сохраняться в media/attachments/user_id/year/month/filename
    return os.path.join(
        'attachments',
        str(instance.entry.owner.id),
        str(instance.entry.entry_date.year),
        str(instance.entry.entry_date.month),
        filename
    )


class Attachment(models.Model):
    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Запись'
    )
    file = models.FileField(
        upload_to=attachment_path,
        verbose_name='Файл'
    )
    caption = models.CharField(max_length=200, blank=True, verbose_name='Подпись')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Загружен')

    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'

    def __str__(self):
        return f"{self.entry.title} - {os.path.basename(self.file.name)}"

    def filename(self):
        return os.path.basename(self.file.name)


class Reminder(models.Model):
    PRIORITY_CHOICES = (
        (1, 'Низкий'),
        (2, 'Средний'),
        (3, 'Высокий'),
    )

    STATUS_CHOICES = (
        ('pending', 'Ожидает'),
        ('completed', 'Выполнено'),
        ('canceled', 'Отменено'),
    )

    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(blank=True, verbose_name='Описание')
    due_date = models.DateField(verbose_name='Срок выполнения')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2, verbose_name='Приоритет')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Теги')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Завершено')

    class Meta:
        verbose_name = 'Напоминание'
        verbose_name_plural = 'Напоминания'
        ordering = ['priority', 'due_date']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.status != 'completed'