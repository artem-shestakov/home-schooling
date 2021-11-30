from django.contrib import admin
from django.db.models import fields

from .models import Day, Lesson, Subject

admin.site.register(Day)
admin.site.register(Lesson)

@admin.register(Subject)
class AuthorAdmin(admin.ModelAdmin):
    pass
