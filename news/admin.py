from django.contrib import admin
from .models import News, Category, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_featured', 'view_count', 'publish_time')
    list_filter = ('is_featured', 'category', 'publish_time')
    list_editable = ('is_featured',)
    search_fields = ('title', 'content', 'author', 'source')
    date_hierarchy = 'publish_time'
    ordering = ('-is_featured', '-publish_time')
    actions = ['mark_as_featured', 'unmark_as_featured']

    @admin.action(description='设为头条')
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'已将 {updated} 条新闻设为头条')

    @admin.action(description='取消头条')
    def unmark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'已取消 {updated} 条新闻的头条标记')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'news', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username', 'news__title')
    date_hierarchy = 'created_at'
