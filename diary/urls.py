from django.urls import path

from .views import (DiaryHomeView, EntryCalendarView, EntryCreateView,
                    EntryDeleteView, EntryDetailView, EntryListView,
                    EntryUpdateView, ProfilePageView, SettingsPageView,
                    StatisticsView, TagCreateView, TagDeleteView, TagListView,
                    TagUpdateView, contacts, faq)

app_name = "diary"


urlpatterns = [
    path("", DiaryHomeView.as_view(), name="index"),
    path("profile/", ProfilePageView.as_view(), name="profile_page"),
    path("settings/", SettingsPageView.as_view(), name="settings"),
    path("entries/", EntryListView.as_view(), name="entry_list"),
    path("entries/create/", EntryCreateView.as_view(), name="entry_create"),
    path("entries/<int:pk>/", EntryDetailView.as_view(), name="entry_detail"),
    path("entries/<int:pk>/update/", EntryUpdateView.as_view(), name="entry_update"),
    path("entries/<int:pk>/delete/", EntryDeleteView.as_view(), name="entry_delete"),
    path("tags/", TagListView.as_view(), name="tag_list"),
    path("tags/create/", TagCreateView.as_view(), name="tag_create"),
    path("tags/<int:pk>/update/", TagUpdateView.as_view(), name="tag_update"),
    path("tags/<int:pk>/delete/", TagDeleteView.as_view(), name="tag_delete"),
    path("calendar/", EntryCalendarView.as_view(), name="entry_calendar"),
    path(
        "calendar/<int:year>/<int:month>/",
        EntryCalendarView.as_view(),
        name="entry_calendar_month",
    ),
    path("statistics/", StatisticsView.as_view(), name="statistics"),
    path("faq/", faq, name="faq"),
    path("contacts/", contacts, name="contacts"),
]
