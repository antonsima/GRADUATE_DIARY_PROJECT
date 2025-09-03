from django.urls import path

from .views import SettingsPageView, ProfilePageView, DiaryHomeView, EntryListView, EntryCreateView, EntryDetailView, \
    EntryUpdateView, EntryDeleteView, TagListView, TagCreateView, TagUpdateView, TagDeleteView

app_name = 'diary'


urlpatterns = [
    path('', DiaryHomeView.as_view(), name='index'),
    path('profile/', ProfilePageView.as_view(), name='profile_page'),

    path('entries/', EntryListView.as_view(), name='entry_list'),
    path('entries/create/', EntryCreateView.as_view(), name='entry_create'),
    path('entries/<int:pk>/', EntryDetailView.as_view(), name='entry_detail'),
    path('entries/<int:pk>/update/', EntryUpdateView.as_view(), name='entry_update'),
    path('entries/<int:pk>/delete/', EntryDeleteView.as_view(), name='entry_delete'),

    path('tags/', TagListView.as_view(), name='tag_list'),
    path('tags/create/', TagCreateView.as_view(), name='tag_create'),
    path('tags/<int:pk>/update/', TagUpdateView.as_view(), name='tag_update'),
    path('tags/<int:pk>/delete/', TagDeleteView.as_view(), name='tag_delete'),

    path('settings/', SettingsPageView.as_view(), name='settings'),
]
