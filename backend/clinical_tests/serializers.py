from rest_framework import serializers
from .models import Test, Question, ClinicalSession, Response
from final_prediction.models import FinalPrediction

class FinalPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalPrediction
        fields = ['id', 'final_prediction', 'recommended_tests', 'created_at']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'order', 'options', 'is_open_ended']

class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = ['id', 'name', 'scoring_rules', 'is_placeholder', 'questions']  # Added 'questions'

class ResponseSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = Response
        fields = ['id', 'question', 'selected_option', 'open_ended_answer', 'follow_up_questions', 'responded_at']

class ClinicalSessionSerializer(serializers.ModelSerializer):
    test = TestSerializer(read_only=True)
    prediction = FinalPredictionSerializer(read_only=True)
    responses = ResponseSerializer(many=True, read_only=True)

    class Meta:
        model = ClinicalSession
        fields = ['id', 'test', 'prediction', 'started_at', 'is_complete', 'total_score', 'severity', 'responses']