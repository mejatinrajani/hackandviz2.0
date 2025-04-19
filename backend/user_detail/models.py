from django.conf import settings
from django.db import models

class UserResponse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.TextField()
    response = models.TextField()
    is_followup = models.BooleanField(default=False)  # Indicates if it's a follow-up
    parent_response = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='followups')
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of response creation

    def __str__(self):
        response_type = '[Follow-up]' if self.is_followup else '[Main]'
        return f"{response_type} {self.question[:30]} - {self.user}"

    class Meta:
        ordering = ['created_at']  # Orders responses by creation time
