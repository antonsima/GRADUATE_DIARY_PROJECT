import os
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from dotenv import load_dotenv

from diary.models import Entry, Tag

load_dotenv(override=True)

User = get_user_model()


class Command(BaseCommand):
    help = "Load initial data (standard tags and sample entries)"

    def handle(self, *args, **options):
        # Получаем email и пароль из переменных окружения
        admin_email = os.getenv("TEST_EMAIL")
        admin_password = os.getenv("TEST_PASSWORD")

        # Проверяем существование суперпользователя
        if not User.objects.filter(is_superuser=True).exists():
            # Пытаемся найти пользователя с email
            try:
                admin_user = User.objects.get(email=admin_email)
                # Если пользователь найден, но не суперпользователь - повышаем права
                if not admin_user.is_superuser:
                    admin_user.is_superuser = True
                    admin_user.is_staff = True
                    admin_user.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated existing user to superuser: {admin_email}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Superuser already exists: {admin_email}")
                    )
            except User.DoesNotExist:
                # Создаем нового суперпользователя если пользователь не существует
                admin_user = User.objects.create_superuser(
                    email=admin_email, password=admin_password
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Created new superuser: {admin_email}")
                )
        else:
            admin_user = User.objects.filter(is_superuser=True).first()
            self.stdout.write(
                self.style.WARNING(f"Using existing superuser: {admin_user.email}")
            )

        # Стандартные теги с цветами из COLOR_PALETTE
        standard_tags = [
            ("Работа", "#ca1d23"),  # Красный
            ("Учеба", "#003d92"),  # Синий
            ("Личное", "#6aa958"),  # Зеленый
            ("Идеи", "#e7949e"),  # Розовый
            ("Книги", "#72757a"),  # Серый
            ("Здоровье", "#6aa958"),  # Зеленый
            ("Путешествия", "#003d92"),  # Синий
            ("Финансы", "#72757a"),  # Серый
        ]

        created_tags = []

        # Создаем стандартные теги без владельца
        for name, color in standard_tags:
            # Генерируем слаг
            tag_slug = slugify(name, allow_unicode=True)

            # Проверяем, существует ли тег с таким слагом
            tag, created = Tag.objects.get_or_create(
                slug=tag_slug,
                defaults={
                    "name": name,
                    "color": color,
                    "owner": None,  # Стандартные теги без владельца
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created tag: {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Tag already exists: {name}"))

            created_tags.append(tag)

        # Создаем тестовые записи
        sample_entries = [
            {
                "title": "Мой первый день",
                "content": "Сегодня был замечательный день! Я начал вести этот дневник и очень этому рад.\n\nНадеюсь, "
                           "что буду регулярно записывать свои мысли и впечатления.",
                "mood": 5,
                "tags": ["Личное"],
            },
            {
                "title": "Рабочие задачи",
                "content": "Сегодня на работе нужно было выполнить несколько важных задач:\n\n1. Завершить проект\n2. "
                           "Подготовить отчет\n3. Встретиться с командой\n\nВсе прошло успешно!",
                "mood": 4,
                "tags": ["Работа"],
            },
            {
                "title": "Идея для нового проекта",
                "content": "Сегодня пришла в голову интересная идея для нового проекта. Нужно записать ее пока не "
                           "забыл:\n\n- Создать приложение для учета личных финансов\n- "
                           "Добавить возможность анализа расходов\n- Синхронизация с банковскими картами",
                "mood": 5,
                "tags": ["Идеи", "Финансы"],
            },
            {
                "title": "Прочитал интересную книгу",
                "content": 'Закончил читать "Атомные привычки". Очень понравилась идея о том, '
                           'что небольшие ежедневные изменения могут привести к значительным результатам '
                           'в долгосрочной перспективе.',
                "mood": 4,
                "tags": ["Книги", "Личное"],
            },
            {
                "title": "Планы на отпуск",
                "content": "Начинаю планировать отпуск. Хочу посетить:\n\n- Италию\n- Грецию\n- Испанию\n\nНужно "
                           "изучить варианты перелета и проживания.",
                "mood": 5,
                "tags": ["Путешествия"],
            },
            {
                "title": "Посетил спортзал",
                "content": "После долгого перерыва снова посетил спортзал. Чувствую себя уставшим, но довольным. "
                           "Нужно сделать это привычкой!",
                "mood": 4,
                "tags": ["Здоровье"],
            },
            {
                "title": "Изучаю Django",
                "content": "Потратил несколько часов на изучение Django. Очень мощный фреймворк! Особенно "
                           "понравилась система ORM и административная панель.",
                "mood": 4,
                "tags": ["Учеба", "Работа"],
            },
            {
                "title": "Финансовый отчет за месяц",
                "content": "Проанализировал расходы за прошлый месяц. Нужно сократить траты на развлечения и "
                           "больше откладывать на будущие цели.",
                "mood": 3,
                "tags": ["Финансы"],
            },
        ]

        # Создаем записи
        for i, entry_data in enumerate(sample_entries):
            # Создаем запись с датой в прошлом (от 1 до 30 дней назад)
            entry_date = date.today() - timedelta(days=30 - i)

            entry = Entry.objects.create(
                title=entry_data["title"],
                content=entry_data["content"],
                entry_date=entry_date,
                mood=entry_data["mood"],
                owner=admin_user,
            )

            # Добавляем теги к записи
            for tag_name in entry_data["tags"]:
                tag = Tag.objects.get(name=tag_name)
                entry.tags.add(tag)

            self.stdout.write(
                self.style.SUCCESS(f'Created entry: {entry_data["title"]}')
            )

        self.stdout.write(
            self.style.SUCCESS("Successfully loaded initial data with sample entries")
        )
