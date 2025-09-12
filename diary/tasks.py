import logging

from celery import shared_task

from users.models import User
from .models import Entry
from .services import send_telegram_message

logger = logging.getLogger(__name__)


@shared_task
def send_daily_entry_reminders():
    """
    Отправляет уведомления о записях по выбранным пользователем тегам
    """
    try:
        # Находим пользователей с настроенными уведомлениями
        users = User.objects.filter(
            notification_tags__isnull=False,
            chat_id__isnull=False
        ).distinct().prefetch_related('notification_tags')

        for user in users:
            # Получаем все записи с выбранными тегами
            entries = Entry.objects.filter(
                owner=user,
                tags__in=user.notification_tags.all()
            ).distinct().order_by('-entry_date')

            if not entries:
                continue

            # Формируем сообщение
            message = "📝 *Ваши записи с выбранными тегами:*\n\n"
            for entry in entries:
                message += (
                    f"• *{entry.title}*\n"
                    f"  Дата: {entry.entry_date.strftime('%d.%m.%Y')}\n"
                    f"  Настроение: {entry.get_mood_display()}\n"
                    f"  Теги: {', '.join([tag.name for tag in entry.tags.all()])}\n\n"
                )

            try:
                send_telegram_message(user.chat_id, message)
                logger.info(f"Отправлено уведомление для {user.email}")
            except Exception as e:
                logger.error(f"Ошибка отправки для {user.email}: {str(e)}")

    except Exception as e:
        logger.error(f"Ошибка в задаче send_daily_entry_reminders: {str(e)}")
