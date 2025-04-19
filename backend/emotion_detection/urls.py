from django.urls import path
from .views import DetectEmotionAndPredictDisorderView

urlpatterns = [
    path('detect-emotion/', DetectEmotionAndPredictDisorderView.as_view(), name='detect-emotion'),
]
