from django.contrib import admin

from diary.models import Entry, Tag
from users.models import User

admin.site.register(User)
admin.site.register(Entry)
admin.site.register(Tag)
