from datetime import date

from django.db.models import Count, Q
from django.utils import timezone

from diary.models import Entry, Tag


def diary_context(request):
    context = {}

    if request.user.is_authenticated:
        user = request.user

        sidebar_popular_tags = (
            Tag.objects.filter(Q(owner=user) | Q(owner__isnull=True), entry__owner=user)
            .annotate(count=Count("entry"))
            .order_by("-count")[:10]
        )

        entries = Entry.objects.filter(owner=user)
        sidebar_total_entries = entries.count()

        now = timezone.now()
        sidebar_monthly_entries = entries.filter(
            entry_date__year=now.year, entry_date__month=now.month
        ).count()

        today = timezone.now().date()
        sidebar_today_entries = entries.filter(entry_date=today).count()

        context.update(
            {
                "sidebar_popular_tags": sidebar_popular_tags,
                "sidebar_total_entries": sidebar_total_entries,
                "sidebar_monthly_entries": sidebar_monthly_entries,
                "sidebar_today_entries": sidebar_today_entries,
            }
        )
    else:
        context.update(
            {
                "sidebar_popular_tags": [],
                "sidebar_total_entries": 0,
                "sidebar_monthly_entries": 0,
                "sidebar_today_entries": 0,
            }
        )

    return context
