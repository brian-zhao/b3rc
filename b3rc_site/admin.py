from django.contrib import admin
from .models import SiteMedia, CarouselImage


@admin.register(SiteMedia)
class SiteMediaAdmin(admin.ModelAdmin):
    list_display = ('slot', 'file', 'alt_text', 'updated_at')
    list_editable = ('file', 'alt_text')
    ordering = ('slot',)


@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ('order', 'image', 'alt_text')
    list_display_links = None
    list_editable = ('order', 'image', 'alt_text')
    ordering = ('order',)
