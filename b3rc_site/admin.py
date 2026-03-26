from django.contrib import admin
from .models import SiteMedia


@admin.register(SiteMedia)
class SiteMediaAdmin(admin.ModelAdmin):
    list_display = ('slot', 'file', 'alt_text', 'updated_at')
    list_editable = ('file', 'alt_text')
    ordering = ('slot',)
