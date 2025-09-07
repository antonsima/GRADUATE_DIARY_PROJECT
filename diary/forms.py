from django import forms
from django.db.models import Q
from django.utils import timezone

from .models import Entry, Tag


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ["title", "content", "entry_date", "mood", "tags"]
        widgets = {
            "entry_date": forms.DateInput(attrs={"type": "date"}),
            # "content": forms.Textarea(attrs={"rows": 15}),
        }
        labels = {
            "title": "Заголовок",
            "content": "Содержание (Markdown)",
            "entry_date": "Дата записи",
            "mood": "Настроение",
            "tags": "Теги",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            # Ограничиваем выбор тегов только тегами пользователя и общими
            self.fields["tags"].queryset = Tag.objects.filter(
                Q(owner=user) | Q(owner__isnull=True)
            )

            # Устанавливаем текущую дату по умолчанию
            self.fields["entry_date"].initial = forms.fields.DateField().to_python(
                timezone.now().date()
            )


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name", "color"]
        labels = {
            "name": "Название тега",
            "color": "Цвет",
        }
        help_texts = {
            "name": "Минимум 2 символа",
        }
