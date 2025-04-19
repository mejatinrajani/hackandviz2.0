from django.urls import path
from .views import recommend

urlpatterns = [
    path('api/recommend/', recommend, name='recommend'),
]