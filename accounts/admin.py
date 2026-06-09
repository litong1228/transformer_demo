from django.contrib import admin
from .models import Bookmark


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'news', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'news__title')
    raw_id_fields = ('user', 'news')
    date_hierarchy = 'created_at'
