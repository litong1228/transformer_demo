from django.contrib import admin
from .models import ClassificationResult, BatchClassification


@admin.register(ClassificationResult)
class ClassificationResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'predicted_category', 'confidence', 'created_at')
    list_filter = ('predicted_category', 'created_at')
    search_fields = ('text', 'predicted_category')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(BatchClassification)
class BatchClassificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'file_name', 'total_count', 'success_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('file_name',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
