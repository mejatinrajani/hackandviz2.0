# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("start/", views.start_conversation, name="start_conversation"),
    path("submit_answer/", views.submit_answer, name="submit_answer"),
    path("submit_followup/", views.submit_followup, name="submit_followup"),
]
