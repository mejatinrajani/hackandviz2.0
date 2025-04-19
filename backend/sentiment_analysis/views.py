from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging
from .audio_model import analyze_audio_sentiment
from .serializers import SentimentInputSerializer
from .text_model import analyze_text
from transformers import AutoFeatureExtractor, Wav2Vec2ForSequenceClassification
import torchaudio.transforms as T
from final_prediction.models import UserPrediction

# Suppress Wav2Vec2 warning
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

# Load audio model only once
audio_model_name = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
extractor = AutoFeatureExtractor.from_pretrained(audio_model_name)
audio_model = Wav2Vec2ForSequenceClassification.from_pretrained(audio_model_name)
label_mapping = audio_model.config.id2label

logger = logging.getLogger(__name__)

@api_view(['POST'])
def analyze_user_text(request):
    serializer = SentimentInputSerializer(data=request.data)
    if serializer.is_valid():
        text = serializer.validated_data["text"]
        result = analyze_text(text)
        
        text_prediction = result["final_disorders"][0] if result["final_disorders"] else "No significant disorder"
        text_disorders = [{'disorder': d, 'score': result["disorder_score"][d]} for d in result["final_disorders"]]
        
        user = request.user
        if user.is_authenticated:
            user_prediction, created = UserPrediction.objects.get_or_create(
                user=user,
                defaults={
                    'text_emotion': text_prediction,
                    'text_confidence': 0.7,
                    'text_disorders': text_disorders
                }
            )
            if not created:
                user_prediction.text_emotion = text_prediction
                user_prediction.text_confidence = 0.7
                user_prediction.text_disorders = text_disorders
                user_prediction.save()

        return Response({
            **result,
            "text_prediction": text_prediction
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def audio_sentiment_view(request):
    audio_file = request.FILES.get("audio")
    if not audio_file:
        return Response({"error": "No audio file provided."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        predicted_emotion, confidence, disorder_scores_with_tests = analyze_audio_sentiment(audio_file)

        if predicted_emotion is None:
            return Response({"error": "Error in audio analysis."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        audio_prediction = max(
            disorder_scores_with_tests.items(),
            key=lambda x: x[1]['score']
        )[0] if disorder_scores_with_tests else "No significant disorder"
        audio_disorders = [{'disorder': k, 'score': v['score'], 'test': v['test']} for k, v in disorder_scores_with_tests.items()]

        user = request.user
        if user.is_authenticated:
            user_prediction, created = UserPrediction.objects.get_or_create(
                user=user,
                defaults={
                    'audio_emotion': audio_prediction,
                    'audio_confidence': confidence,
                    'audio_disorders': audio_disorders
                }
            )
            if not created:
                user_prediction.audio_emotion = audio_prediction
                user_prediction.audio_confidence = confidence
                user_prediction.audio_disorders = audio_disorders
                user_prediction.save()

        return Response({
            "predicted_emotion": predicted_emotion,
            "confidence": confidence,
            "disorder_scores_with_tests": disorder_scores_with_tests,
            "audio_prediction": audio_prediction
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)