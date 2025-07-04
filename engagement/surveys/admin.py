from django.contrib import admin
from .models import Survey, Theme, Question


class ThemeInline(admin.TabularInline):
    model = Theme
    extra = 0


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'organization__name']
    inlines = [ThemeInline]


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['name', 'survey', 'order']
    list_filter = ['survey__organization']
    search_fields = ['name', 'survey__title']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text_preview', 'theme', 'order']
    list_filter = ['theme__survey__organization']
    search_fields = ['text', 'theme__name']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Question Text'
