from django.contrib import admin
from .models import Survey, Theme, Question, SurveyResponse, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ['question', 'rating']


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


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'created_at', 'completed_at', 'answer_count']
    list_filter = ['organization', 'created_at', 'completed_at']
    search_fields = ['user__email', 'organization__name']
    readonly_fields = ['created_at', 'completed_at']
    inlines = [AnswerInline]
    
    def answer_count(self, obj):
        return obj.answers.count()
    answer_count.short_description = 'Answers'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['response_user', 'organization', 'question_preview', 'rating', 'created_at']
    list_filter = ['rating', 'response__organization', 'response__created_at']
    search_fields = ['response__user__email', 'question__text']
    
    def response_user(self, obj):
        return obj.response.user.email
    response_user.short_description = 'User'
    
    def organization(self, obj):
        return obj.response.organization.name
    organization.short_description = 'Organization'
    
    def question_preview(self, obj):
        return obj.question.text[:40] + '...' if len(obj.question.text) > 40 else obj.question.text
    question_preview.short_description = 'Question'
    
    def created_at(self, obj):
        return obj.response.created_at
    created_at.short_description = 'Response Date'
