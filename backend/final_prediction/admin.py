from django.contrib import admin
from .models import FinalPrediction

@admin.register(FinalPrediction)
class FinalPredictionAdmin(admin.ModelAdmin):
    list_display = ("user", "facial_prediction", "audio_prediction", "text_prediction", "final_prediction", "timestamp")
