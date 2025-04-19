from django.urls import path
from .views import ListTests, StartClinicalTestFromPrediction, ContinueClinicalTest, DownloadReport

urlpatterns = [
    path('tests/', ListTests.as_view(), name='list-tests'),
    path('start-test-from-prediction/', StartClinicalTestFromPrediction.as_view(), name='start-test-from-prediction'),
    path('continue-test/', ContinueClinicalTest.as_view(), name='continue-test'),
    path('download-report/<int:session_id>/', DownloadReport.as_view(), name='download-report'),
]