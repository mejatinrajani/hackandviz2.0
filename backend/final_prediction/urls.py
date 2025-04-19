from django.urls import path
from .views import FinalPredictionView

urlpatterns = [
    path("predict/", FinalPredictionView.as_view(), name="final-prediction"),
]
