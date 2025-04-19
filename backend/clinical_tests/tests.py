import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from clinical_tests.models import ClinicalSession
from unittest.mock import patch, MagicMock
from io import BytesIO

# Use get_user_model() to support custom user models
User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    # Create a user with required fields for CustomUser, including username
    return User.objects.create_user(
        username='testuser',
        name='Test User',
        email='testuser@example.com',
        phone_number='1234567890',
        password='testpass'
    )

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def test_session(user):
    return ClinicalSession.objects.create(
        user=user,
        test_name="Beck Depression Inventory (BDI)",
        gemini_response_log=[],
        completed=False
    )

# Mock GeminiChatBot to prevent model initialization
@pytest.fixture
def mock_gemini_chatbot():
    with patch('user_detail.gemini_service.GeminiChatBot') as MockChatBot:
        mock_instance = MockChatBot.return_value
        mock_instance.chat.side_effect = lambda x: (
            "Question 1: How often do you feel sad?" if "Beck Depression Inventory" in x
            else "Score: 15, Severity: Mild" if x == "user response"
            else "Next question or response"
        )
        mock_instance.chat_history = []
        yield mock_instance

# Mock generate_clinical_report_pdf
@pytest.fixture
def mock_generate_pdf():
    with patch('clinical_tests.views.generate_clinical_report_pdf') as mock_pdf:
        mock_pdf.return_value = BytesIO(b"Fake PDF content")
        yield mock_pdf

@pytest.mark.django_db
class TestClinicalTestAPI:
    def test_start_clinical_test_success(self, authenticated_client, mock_gemini_chatbot):
        url = reverse('start')
        data = {"test_name": "Beck Depression Inventory (BDI)"}
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == 200
        assert response.data['message'] == "Test started."
        assert 'session_id' in response.data
        assert response.data['gemini_message'] == "Question 1: How often do you feel sad?"

        session = ClinicalSession.objects.get(id=response.data['session_id'])
        assert session.user == authenticated_client.handler._force_user
        assert session.test_name == "Beck Depression Inventory (BDI)"
        assert len(session.gemini_response_log) == 1
        assert session.gemini_response_log[0]['content'] == "Question 1: How often do you feel sad?"

    def test_start_clinical_test_unauthenticated(self, api_client):
        url = reverse('start')
        data = {"test_name": "Beck Depression Inventory (BDI)"}
        response = api_client.post(url, data, format='json')

        assert response.status_code == 401
        assert 'Authentication credentials were not provided' in response.data['detail']

    def test_continue_clinical_test_success(self, authenticated_client, test_session, mock_gemini_chatbot):
        url = reverse('continue', args=[test_session.id])
        data = {"message": "user response"}
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == 200
        assert response.data['gemini_message'] == "Score: 15, Severity: Mild"
        assert response.data['completed'] is True

        test_session.refresh_from_db()
        assert test_session.completed is True
        assert test_session.score == 15
        assert test_session.severity == "Mild"
        assert len(test_session.gemini_response_log) == 2
        assert test_session.gemini_response_log[0]['content'] == "user response"
        assert test_session.gemini_response_log[1]['content'] == "Score: 15, Severity: Mild"

    def test_continue_clinical_test_invalid_session(self, authenticated_client):
        url = reverse('continue', args=[999])
        data = {"message": "user response"}
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == 404

    def test_continue_clinical_test_unauthenticated(self, api_client, test_session):
        url = reverse('continue', args=[test_session.id])
        data = {"message": "user response"}
        response = api_client.post(url, data, format='json')

        assert response.status_code == 401

    def test_download_report_success(self, authenticated_client, test_session, mock_generate_pdf):
        test_session.completed = True
        test_session.score = 15
        test_session.severity = "Mild"
        test_session.save()

        url = reverse('download_report', args=[test_session.id])
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'
        assert f'clinical_report_{test_session.test_name}_{test_session.id}.pdf' in response['Content-Disposition']
        assert response.content == b"Fake PDF content"

    def test_download_report_invalid_session(self, authenticated_client):
        url = reverse('download_report', args=[999])
        response = authenticated_client.get(url)

        assert response.status_code == 404

    def test_download_report_unauthenticated(self, api_client, test_session):
        url = reverse('download_report', args=[test_session.id])
        response = api_client.get(url)

        assert response.status_code == 401