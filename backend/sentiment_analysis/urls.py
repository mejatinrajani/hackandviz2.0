from django.urls import path
from .views import audio_sentiment_view
from .views import analyze_user_text

urlpatterns = [
    path('text/', analyze_user_text, name='analyze_text'),
    path("audio/", audio_sentiment_view, name="audio_sentiment"),  # Ensure this is correctly mapped
]
