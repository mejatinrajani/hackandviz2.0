from django.db import models
from django.conf import settings
from final_prediction.models import FinalPrediction

class Test(models.Model):
    name = models.CharField(max_length=100, unique=True)
    scoring_rules = models.TextField()
    is_placeholder = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField()
    options = models.JSONField()
    is_open_ended = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']
        unique_together = ['test', 'order']

    def __str__(self):
        return f"{self.test.name} Q{self.order}"

class ClinicalSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    prediction = models.ForeignKey(FinalPrediction, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    total_score = models.FloatField(null=True, blank=True)
    severity = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.test.name}"

class Response(models.Model):
    session = models.ForeignKey(ClinicalSession, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.JSONField(null=True, blank=True)
    open_ended_answer = models.TextField(null=True, blank=True)
    follow_up_questions = models.JSONField(null=True, blank=True)
    responded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session} - Q{self.question.order}"