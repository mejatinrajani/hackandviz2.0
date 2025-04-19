from django.contrib import admin
from .models import Test, Question, ClinicalSession, Response

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_placeholder', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_placeholder',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('test', 'order', 'text_preview', 'is_open_ended')
    search_fields = ('text',)
    list_filter = ('test__name', 'is_open_ended')
    
    def text_preview(self, obj):
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    text_preview.short_description = 'Question Text'

@admin.register(ClinicalSession)
class ClinicalSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_test_name', 'total_score', 'severity', 'is_complete', 'started_at')
    search_fields = ('user__username', 'test__name')
    list_filter = ('is_complete', 'test__name', 'severity')
    readonly_fields = ('started_at', 'completed_at')
    
    def get_test_name(self, obj):
        return obj.test.name
    get_test_name.short_description = 'Test Name'

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('session', 'question_order', 'response_preview', 'responded_at')
    search_fields = ('session__user__username', 'question__text')
    list_filter = ('session__test__name',)
    
    def question_order(self, obj):
        return obj.question.order
    question_order.short_description = 'Question Order'
    
    def response_preview(self, obj):
        answer = obj.open_ended_answer or (obj.selected_option['text'] if obj.selected_option else 'No response')
        return answer[:50] + ('...' if len(answer) > 50 else '')
    response_preview.short_description = 'Response'