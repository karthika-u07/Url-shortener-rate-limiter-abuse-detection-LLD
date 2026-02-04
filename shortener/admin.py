from django.contrib import admin
from .models import ShortURL

@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_url', 'short_code', 'created_at', 'clicks')
    search_fields = ('original_url', 'short_code')
    readonly_fields = ('created_at', 'clicks')
