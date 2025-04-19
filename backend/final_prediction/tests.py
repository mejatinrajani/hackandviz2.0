import pytest
import warnings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from final_prediction.models import FinalPrediction, UserPrediction
from final_prediction.serializers import FinalPredictionSerializer
import datetime
from django.urls import reverse

# Suppress TensorFlow warning
warnings.filterwarnings('ignore', category=DeprecationWarning)

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        name='Test User',
        phone_number='+1234567890'
    )

@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
class TestFinalPredictionAPI:
    def test_unauthenticated_access(self, client):
        url = reverse('final-prediction')
        response = client.post(url, {})
        assert response.status_code == 401
        assert 'Authentication credentials were not provided' in str(response.data)

    def test_missing_predictions(self, client, user):
        client.force_authenticate(user=user)
        response = client.post('/final/predict/', {})  # Updated URL
        assert response.status_code == 400
        assert 'All three predictions' in str(response.data)

    def test_valid_prediction(self, client, user):
        client.force_authenticate(user=user)
        data = {
            'facial_prediction': 'Depression',
            'audio_prediction': 'Depression',
            'text_prediction': 'Anxiety'
        }
        response = client.post('/final/predict/', data)  # Updated URL
        assert response.status_code == 200
        assert response.data['final_prediction'] == 'Depression'
        assert 'BDI' in response.data['recommended_test']
        prediction = FinalPrediction.objects.first()
        assert prediction.user == user
        assert prediction.final_prediction == 'Depression'

    def test_prediction_tie(self, client, user):
        client.force_authenticate(user=user)
        data = {
            'facial_prediction': 'Anxiety',
            'audio_prediction': 'Depression',
            'text_prediction': 'Anxiety'
        }
        response = client.post('/final/predict/', data)  # Updated URL
        assert response.data['final_prediction'] == 'Anxiety'

    def test_unknown_disorder(self, client, user):
        client.force_authenticate(user=user)
        data = {
            'facial_prediction': 'Unknown',
            'audio_prediction': 'Unknown',
            'text_prediction': 'Unknown'
        }
        response = client.post('/final/predict/', data)  # Updated URL
        assert response.data['recommended_test'] == 'General Psychological Screening'

@pytest.mark.django_db
class TestModels:
    def test_final_prediction_str(self, user):
        prediction = FinalPrediction.objects.create(
            user=user,
            facial_prediction='Depression',
            audio_prediction='Anxiety',
            text_prediction='Stress',
            final_prediction='Depression',
            recommended_tests='BDI'
        )
        assert user.email in str(prediction)

    def test_user_prediction_creation(self, user):
        user_prediction = UserPrediction.objects.create(user=user)
        assert user_prediction.text_emotion is None
        assert isinstance(user_prediction.timestamp, datetime.datetime)

@pytest.mark.django_db
class TestSerializers:
    def test_final_prediction_serialization(self, user):
        prediction = FinalPrediction.objects.create(
            user=user,
            facial_prediction='Anxiety',
            audio_prediction='Anxiety',
            text_prediction='Anxiety',
            final_prediction='Anxiety',
            recommended_tests='GAD-7'
        )
        serializer = FinalPredictionSerializer(prediction)
        assert 'final_prediction_message' in serializer.data
        assert 'Anxiety' in serializer.data['final_prediction_message']