from django import forms
from .models import Entry, Tag, Mood
from markdownx.widgets import MarkdownxWidget

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['title', 'content', 'entry_date', 'is_public', 'mood', 'tags']
        widgets = {
            'content': MarkdownxWidget(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'entry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mood': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'content': 'Содержание (Markdown)',
        }