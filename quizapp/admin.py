from django.contrib import admin

from .models import LearningMaterial


@admin.register(LearningMaterial)
class LearningMaterialAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'field',
        'is_active',
        'updated_at',
    )

    list_filter = (
        'field',
        'is_active',
    )

    search_fields = (
        'title',
        'content',
    )