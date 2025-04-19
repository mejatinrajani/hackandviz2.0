from django.db import models
from django.conf import settings

# Use the custom user model via settings.AUTH_USER_MODEL
class FinalPrediction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    facial_prediction = models.CharField(max_length=100)
    audio_prediction = models.CharField(max_length=100)
    text_prediction = models.CharField(max_length=100)
    final_prediction = models.CharField(max_length=200)
    recommended_tests = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FinalPrediction for {self.user.email}"


class UserPrediction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Text Prediction fields
    text_emotion = models.CharField(max_length=255, null=True, blank=True)
    text_confidence = models.FloatField(null=True, blank=True)
    text_disorders = models.JSONField(null=True, blank=True)

    # Audio Prediction fields
    audio_emotion = models.CharField(max_length=255, null=True, blank=True)
    audio_confidence = models.FloatField(null=True, blank=True)
    audio_disorders = models.JSONField(null=True, blank=True)

    # Facial Emotion Prediction fields
    video_emotion = models.CharField(max_length=255, null=True, blank=True)
    video_confidence = models.FloatField(null=True, blank=True)
    video_disorders = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Prediction for {self.user} at {self.timestamp}"


class CombinedPrediction(models.Model):
    user_prediction = models.OneToOneField(UserPrediction, on_delete=models.CASCADE)
    final_disorders = models.JSONField()
    final_prediction_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Final Prediction for {self.user_prediction.user}"
