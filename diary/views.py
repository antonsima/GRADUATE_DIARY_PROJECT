import calendar
from collections import defaultdict
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from diary.forms import EntryForm, TagForm
from diary.models import Entry, Tag


class DiaryHomeView(TemplateView):
    template_name = "diary/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            user = self.request.user

            entries = Entry.objects.filter(owner=user)

            recent_entries = entries.order_by("-entry_date")[:6]

            tags = Tag.objects.filter(
                Q(owner=self.request.user) | Q(owner__isnull=True)
            ).annotate(
                entry_count=Count('entry', filter=Q(entry__owner=self.request.user))
            )

            tag_counts = {tag.id: tag.entry_count for tag in tags}
            context['tag_counts'] = tag_counts

            mood_stats_data = (
                entries.values("mood").annotate(count=Count("id")).order_by("mood")
            )
            total_with_mood = sum(item["count"] for item in mood_stats_data)

            mood_colors = {
                1: "#ca1d23",
                2: "#e7949e",
                3: "#72757a",
                4: "#a8927c",
                5: "#6aa958",
            }

            mood_stats = []
            for item in mood_stats_data:
                mood_value = item["mood"]
                count = item["count"]
                percentage = (
                    (count / total_with_mood * 100) if total_with_mood > 0 else 0
                )

                mood_display = next(
                    (
                        display
                        for value, display in Entry.MOOD_LEVEL
                        if value == mood_value
                    ),
                    str(mood_value),
                )

                mood_stats.append(
                    {
                        "mood": mood_value,
                        "mood_display": mood_display,
                        "count": count,
                        "percentage": round(percentage, 1),
                        "color": mood_colors.get(mood_value, "#72757a"),
                    }
                )

            context.update(
                {
                    "recent_entries": recent_entries,
                    "mood_stats": mood_stats,
                    "tag_counts": tag_counts,
                }
            )
        else:
            context.update(
                {
                    "total_entries": 0,
                    "monthly_entries": 0,
                    "today_entries": 0,
                    "recent_entries": [],
                    "mood_stats": [],
                    "popular_tags": [],
                    "tag_counts": {}
                }
            )

        return context


class ProfilePageView(View):
    def get(self, request):
        return render(request, "diary/profile.html")


class SettingsPageView(View):
    def get(self, request):
        all_tags = Tag.objects.all()
        return render(request, "diary/settings.html", {"all_tags": all_tags})

    def post(self, request):
        user = request.user
        print(f"User: {user}")
        print(f"Files: {request.FILES}")

        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)

        # Обработка chat_id для Telegram
        chat_id = request.POST.get("chat_id")
        if chat_id:
            try:
                user.chat_id = int(chat_id)
            except (ValueError, TypeError):
                messages.error(request, _("ID чата должен быть числом"))

        # Обработка выбранных тегов для уведомлений
        notification_tag_ids = request.POST.getlist("notification_tags")
        try:
            notification_tags = Tag.objects.filter(id__in=notification_tag_ids)
            user.notification_tags.set(notification_tags)
        except Exception as e:
            messages.error(request, _(f"Ошибка при сохранении тегов уведомлений: {e}"))

        if "avatar" in request.FILES:
            avatar = request.FILES["avatar"]
            print(f"Avatar file: {avatar}")
            print(f"Avatar size: {avatar.size}")
            print(f"Avatar name: {avatar.name}")

            if avatar.size > 2 * 1024 * 1024:
                messages.error(request, _("Размер файла не должен превышать 2MB"))
            else:
                valid_extensions = [".jpg", ".jpeg", ".png", ".gif"]
                import os

                ext = os.path.splitext(avatar.name)[1].lower()

                if ext not in valid_extensions:
                    messages.error(
                        request, _("Поддерживаются только JPEG, PNG и GIF файлы")
                    )
                else:
                    if user.avatar:
                        user.avatar.delete(save=False)
                    user.avatar = avatar
                    messages.success(request, _("Аватар успешно обновлен"))

        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        if password:
            if password != password2:
                messages.error(request, _("Пароли не совпадают"))
            else:
                user.set_password(password)
                messages.success(request, _("Пароль успешно изменен"))
                update_session_auth_hash(request, user)

        try:
            user.save()
            messages.success(request, _("Настройки успешно сохранены"))
        except Exception as e:
            messages.error(request, _(f"Ошибка при сохранении настроек {e}"))

        return redirect("diary:settings")


class EntryListView(LoginRequiredMixin, ListView):
    model = Entry
    template_name = "diary/entry_list.html"
    paginate_by = 10
    context_object_name = "entries"

    def get_queryset(self):
        queryset = Entry.objects.filter(owner=self.request.user)

        tag_slug = self.request.GET.get("tag")
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        mood_id = self.request.GET.get("mood")
        if mood_id:
            queryset = queryset.filter(mood=mood_id)

        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(content__icontains=search_query)
            )

        sort_by = self.request.GET.get(
            "sort_by", "-entry_date"
        )
        if sort_by in [
            "entry_date",
            "-entry_date",
            "date_created",
            "-date_created",
            "date_updated",
            "-date_updated",
            "title",
            "-title",
            "word_count",
            "-word_count",
            "mood",
            "-mood",
        ]:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by("-entry_date")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tags = Tag.objects.filter(
            Q(owner=self.request.user) | Q(owner__isnull=True)
        ).annotate(
            entry_count=Count('entry', filter=Q(entry__owner=self.request.user))
        )
        tag_counts = {tag.id: tag.entry_count for tag in tags}
        context["tags"] = tags
        context["tag_counts"] = tag_counts
        context["mood_levels"] = Entry.MOOD_LEVEL

        return context


class EntryDetailView(LoginRequiredMixin, DetailView):
    model = Entry
    template_name = "diary/entry_detail.html"
    context_object_name = "entry"

    def get_queryset(self):
        return Entry.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Аннотируем теги количеством записей текущего пользователя
        tags = Tag.objects.filter(
            Q(owner=self.request.user) | Q(owner__isnull=True)
        ).annotate(
            entry_count=Count('entry', filter=Q(entry__owner=self.request.user))
        )

        # Создаем словарь для быстрого доступа к количеству записей по ID тега
        tag_counts = {tag.id: tag.entry_count for tag in tags}
        context['tag_counts'] = tag_counts

        return context


class EntryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Entry
    form_class = EntryForm
    template_name = "diary/entry_form.html"
    success_message = "Запись успешно создана!"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy("diary:entry_detail", kwargs={"pk": self.object.pk})


class EntryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Entry
    form_class = EntryForm
    template_name = "diary/entry_form.html"
    success_message = "Запись успешно обновлена!"

    def get_queryset(self):
        return Entry.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy("diary:entry_detail", kwargs={"pk": self.object.pk})


class EntryDeleteView(LoginRequiredMixin, DeleteView):
    model = Entry
    template_name = "diary/entry_confirm_delete.html"
    success_url = reverse_lazy("diary:entry_list")
    success_message = "Запись успешно удалена!"

    def get_queryset(self):
        return Entry.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class TagListView(LoginRequiredMixin, ListView):
    model = Tag
    template_name = "diary/tag_list.html"
    context_object_name = "tags"

    def get_queryset(self):
        return Tag.objects.filter(
            Q(owner=self.request.user) | Q(owner__isnull=True)
        ).order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class TagCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = "diary/tag_form.html"
    success_message = "Тег успешно создан!"
    success_url = reverse_lazy("diary:tag_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class TagUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = "diary/tag_form.html"
    success_message = "Тег успешно обновлен!"
    success_url = reverse_lazy("diary:tag_list")

    def get_queryset(self):
        return Tag.objects.filter(owner=self.request.user)


class TagDeleteView(LoginRequiredMixin, DeleteView):
    model = Tag
    template_name = "diary/tag_confirm_delete.html"
    success_url = reverse_lazy("diary:tag_list")
    success_message = "Тег успешно удален!"

    def get_queryset(self):
        return Tag.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class EntryCalendarView(LoginRequiredMixin, TemplateView):
    template_name = "diary/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year = int(self.kwargs.get("year", datetime.now().year))
        month = int(self.kwargs.get("month", datetime.now().month))

        tag_slug = self.request.GET.get("tag")
        mood_id = self.request.GET.get("mood")
        search_query = self.request.GET.get("q")

        cal = calendar.monthcalendar(year, month)

        entries = Entry.objects.filter(
            owner=self.request.user, entry_date__year=year, entry_date__month=month
        )

        if tag_slug:
            entries = entries.filter(tags__slug=tag_slug)
        if mood_id:
            entries = entries.filter(mood=mood_id)
        if search_query:
            entries = entries.filter(
                Q(title__icontains=search_query) | Q(content__icontains=search_query)
            )

        entries_by_day = defaultdict(list)
        for entry in entries:
            entries_by_day[entry.entry_date.day].append(entry)

        if month == 1:
            prev_month = 12
            prev_year = year - 1
        else:
            prev_month = month - 1
            prev_year = year

        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year

        query_params = self.request.GET.copy()
        if "year" in query_params:
            del query_params["year"]
        if "month" in query_params:
            del query_params["month"]
        query_string = query_params.urlencode()

        tags = Tag.objects.filter(
            Q(owner=self.request.user) | Q(owner__isnull=True)
        ).distinct()

        context.update(
            {
                "calendar": cal,
                "year": year,
                "month": month,
                "month_name": calendar.month_name[month],
                "entries_by_day": dict(entries_by_day),
                "prev_year": prev_year,
                "prev_month": prev_month,
                "next_year": next_year,
                "next_month": next_month,
                "query_string": query_string,
                "tags": tags,
                "mood_levels": Entry.MOOD_LEVEL,
            }
        )

        return context


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = "diary/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        entries = Entry.objects.filter(owner=user)

        from django.db.models import Avg

        avg_words = (
            entries.aggregate(avg_words=Avg("word_count"))[
                "avg_words"
            ]
            or 0
        )

        total_tags = (
            Tag.objects.filter(Q(owner=user) | Q(owner__isnull=True), entry__owner=user)
            .distinct()
            .count()
        )

        mood_stats = (
            entries
            .values("mood")
            .annotate(count=Count("id"))
            .order_by("mood")
        )

        tag_stats = (
            Tag.objects.filter(Q(owner=user) | Q(owner__isnull=True), entry__owner=user)
            .annotate(count=Count("entry"))
            .order_by("-count")
        )

        current_year = datetime.now().year
        monthly_stats = (
            Entry.objects.filter(owner=user, entry_date__year=current_year)
            .extra({"month": "EXTRACT(month FROM entry_date)"})
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        context.update(
            {
                "avg_words": avg_words,
                "total_tags": total_tags,
                "mood_stats": mood_stats,
                "tag_stats": tag_stats,
                "monthly_stats": monthly_stats,
                "current_year": current_year,
            }
        )

        return context


def faq(request):
    faq_items = [
        {
            "question": "Как создать новую запись в дневнике?",
            "answer": 'Для создания новой записи нажмите кнопку "Новая запись" в верхней части страницы или на '
                      'боковой панели. Заполните заголовок, содержание, выберите настроение и добавьте теги.',
        },
        {
            "question": "Как добавить изображения к записи?",
            "answer": "В редакторе записи вы можете загружать изображения, используя перетаскивание изображений в"
                      " редактор. Поддерживаются форматы JPG, PNG и GIF.",
        },
        {
            "question": "Как искать записи по тегам?",
            "answer": "На странице всех записей используйте фильтр по тегам в панели поиска. Вы также можете "
                      "кликнуть на любой тег в записи для фильтрации по нему.",
        },
        {
            "question": "Как работает календарь записей?",
            "answer": "Календарь показывает дни, в которые вы делали записи. Кликните на любой день с записью, "
                      "чтобы перейти к просмотру этой записи.",
        },
        {
            "question": "Как создать и управлять тегами?",
            "answer": 'Перейдите в раздел "Теги" через боковое меню. Там вы можете создавать новые теги, '
                      'редактировать существующие и назначать им цвета. Теги помогают организовать ваши '
                      'записи по темам.',
        },
        {
            "question": "Как работает статистика?",
            "answer": 'В разделе "Статистика" вы можете увидеть обзор вашей активности: количество записей, '
                      'распределение по настроениям, популярные теги и активность по месяцам. Это помогает '
                      'отслеживать ваши привычки и настроения.',
        },
        {
            "question": "Можно ли редактировать старые записи?",
            "answer": 'Да, вы можете редактировать любую запись. Просто откройте запись и нажмите кнопку '
                      '"Редактировать". Все изменения сохранят исходную дату создания, но обновят дату изменения.',
        },
        {
            "question": "Как работает поиск по записям?",
            "answer": "На странице всех записей есть строка поиска, где вы можете искать по заголовкам и "
                      "содержимому записей. Вы также можете использовать фильтры по тегам, настроению и сортировке.",
        },
        {
            "question": "Можно ли экспортировать свои записи?",
            "answer": "В настоящее время функция экспорта находится в разработке. В будущих обновлениях мы "
                      "добавим возможность экспорта записей в различные форматы (PDF, TXT, JSON).",
        },
        {
            "question": "Как изменить настройки профиля?",
            "answer": 'Перейдите в раздел "Настройки" через меню пользователя. Там вы можете изменить имя, '
                      'фамилию, аватар и пароль.',
        },
    ]

    return render(request, "diary/faq.html", {"faq_items": faq_items})


def contacts(request):
    contact_info = {
        "email": "anton_sima@mail.com",
        "phone": "+7 (123) 456-78-90",
        "address": "г. Москва, ул. Примерная, д. 123, офис 456",
        "social_media": [
            {
                "name": "Telegram",
                "url": "https://t.me/baxcha241",
                "icon": "fab fa-telegram",
            },
            {"name": "VK", "url": "https://vk.com/baxcha241", "icon": "fab fa-vk"},
            {
                "name": "YouTube",
                "url": "https://youtube.com/@baxcha241",
                "icon": "fab fa-youtube",
            },
            {
                "name": "Instagram",
                "url": "https://instagram.com/anton_simak",
                "icon": "fab fa-instagram",
            },
        ],
        "support_hours": "Понедельник - Пятница, 9:00 - 18:00 по московскому времени",
    }

    return render(request, "diary/contacts.html", {"contact_info": contact_info})
