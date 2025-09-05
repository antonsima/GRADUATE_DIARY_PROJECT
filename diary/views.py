from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.translation import gettext_lazy as _

from diary.forms import TagForm, EntryForm
from diary.models import Entry, Tag


class DiaryHomeView(TemplateView):
    template_name = 'diary/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # # Последние записи пользователя
        # context['recent_entries'] = Entry.objects.filter(
        #     owner=self.request.user
        # ).order_by('-entry_date')[:5]
        # # Статистика
        # context['total_entries'] = Entry.objects.filter(
        #     owner=self.request.user
        # ).count()
        return context


class ProfilePageView(View):
    def get(self, request):
        return render(request, 'diary/profile.html')


class SettingsPageView(View):
    def get(self, request):
        return render(request, 'diary/settings.html')

    def post(self, request):
        user = request.user
        print(f"User: {user}")
        print(f"Files: {request.FILES}")

        # Обновляем имя и фамилию
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)

        # Обрабатываем загрузку аватара
        if 'avatar' in request.FILES:
            avatar = request.FILES['avatar']
            print(f"Avatar file: {avatar}")
            print(f"Avatar size: {avatar.size}")
            print(f"Avatar name: {avatar.name}")

            # Валидация размера файла
            if avatar.size > 2 * 1024 * 1024:
                messages.error(request, _('Размер файла не должен превышать 2MB'))
            else:
                # Валидация типа файла
                valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
                import os
                ext = os.path.splitext(avatar.name)[1].lower()

                if ext not in valid_extensions:
                    messages.error(request, _('Поддерживаются только JPEG, PNG и GIF файлы'))
                else:
                    # Удаляем старый аватар если он существует
                    if user.avatar:
                        user.avatar.delete(save=False)
                    # Сохраняем новый аватар
                    user.avatar = avatar
                    messages.success(request, _('Аватар успешно обновлен'))

        # Обрабатываем смену пароля
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if password:
            if password != password2:
                messages.error(request, _('Пароли не совпадают'))
            else:
                user.set_password(password)
                messages.success(request, _('Пароль успешно изменен'))
                # Обновляем сессию чтобы пользователь не разлогинился
                update_session_auth_hash(request, user)

        try:
            user.save()
            messages.success(request, _('Настройки успешно сохранены'))
        except Exception as e:
            messages.error(request, _('Ошибка при сохранении настроек'))

        return redirect('diary:settings')


class EntryListView(LoginRequiredMixin, ListView):
    model = Entry
    template_name = 'diary/entry_list.html'
    paginate_by = 10
    context_object_name = 'entries'

    def get_queryset(self):
        queryset = Entry.objects.filter(owner=self.request.user)

        # Фильтрация по тегу
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        # Фильтрация по настроению
        mood_id = self.request.GET.get('mood')
        if mood_id:
            queryset = queryset.filter(mood=mood_id)

        # Поиск
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )

        return queryset.order_by('-entry_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.filter(
            Q(owner=self.request.user) | Q(owner__isnull=True)
        )
        context['mood_levels'] = Entry.MOOD_LEVEL

        return context


class EntryDetailView(LoginRequiredMixin, DetailView):
    model = Entry
    template_name = 'diary/entry_detail.html'
    context_object_name = 'entry'

    def get_queryset(self):
        return Entry.objects.filter(owner=self.request.user)


class EntryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Entry
    form_class = EntryForm
    template_name = 'diary/entry_form.html'
    success_message = "Запись успешно создана!"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        # Markdownx автоматически обрабатывает конвертацию через сигналы
        # или метод save модели, поэтому нам не нужно делать это вручную
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('diary:entry_detail', kwargs={'pk': self.object.pk})


class EntryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Entry
    form_class = EntryForm
    template_name = 'diary/entry_form.html'
    success_message = "Запись успешно обновлена!"

    def get_queryset(self):
        return Entry.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('diary:entry_detail', kwargs={'pk': self.object.pk})


class EntryDeleteView(LoginRequiredMixin, DeleteView):
    model = Entry
    template_name = 'diary/entry_confirm_delete.html'
    success_url = reverse_lazy('diary:entry_list')
    success_message = "Запись успешно удалена!"

    def get_queryset(self):
        return Entry.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class TagListView(LoginRequiredMixin, ListView):
    model = Tag
    template_name = 'diary/tag_list.html'
    context_object_name = 'tags'

    def get_queryset(self):
        return Tag.objects.filter(
            Q(owner=self.request.user) | Q(owner__isnull=True)
        ).order_by('name')


class TagCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'diary/tag_form.html'
    success_message = "Тег успешно создан!"
    success_url = reverse_lazy('diary:tag_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class TagUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = 'diary/tag_form.html'
    success_message = "Тег успешно обновлен!"
    success_url = reverse_lazy('diary:tag_list')

    def get_queryset(self):
        return Tag.objects.filter(owner=self.request.user)


class TagDeleteView(LoginRequiredMixin, DeleteView):
    model = Tag
    template_name = 'diary/tag_confirm_delete.html'
    success_url = reverse_lazy('diary:tag_list')
    success_message = "Тег успешно удален!"

    def get_queryset(self):
        return Tag.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)