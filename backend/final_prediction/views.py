from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from final_prediction.models import FinalPrediction, UserPrediction
from django.contrib.auth import get_user_model
import logging

User = get_user_model()

# Set up logging
logger = logging.getLogger(__name__)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from final_prediction.models import FinalPrediction, UserPrediction
from django.contrib.auth import get_user_model
import logging

User = get_user_model()

# Set up logging
logger = logging.getLogger(__name__)

class FinalPredictionView(APIView):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            logger.error("Authentication required: User not authenticated")
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        # Log user details
        logger.debug(f"Processing final prediction for user: {user.email if hasattr(user, 'email') else user.id}")

        # Get the latest UserPrediction for the user
        try:
            user_prediction = UserPrediction.objects.filter(user=user).order_by('-timestamp').first()
            if not user_prediction:
                logger.error(f"No UserPrediction found for user: {user.email if hasattr(user, 'email') else user.id}")
                return Response({
                    "error": "No predictions found for this user. Please complete text, audio, and video predictions first.",
                    "debug": "Ensure /api/sentiment/text/, /api/sentiment/audio/, and /api/emotion/detect-emotion/ are called with the same authenticated user."
                }, status=status.HTTP_400_BAD_REQUEST)
        except UserPrediction.DoesNotExist:
            logger.error(f"UserPrediction does not exist for user: {user.email if hasattr(user, 'email') else user.id}")
            return Response({
                "error": "No predictions found for this user. Please complete text, audio, and video predictions first.",
                "debug": "Ensure /api/sentiment/text/, /api/sentiment/audio/, and /api/emotion/detect-emotion/ are called with the same authenticated user."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Extract predictions
        facial_prediction = user_prediction.video_emotion
        audio_prediction = user_prediction.audio_emotion
        text_prediction = user_prediction.text_emotion

        # Log extracted predictions
        logger.debug(f"Extracted predictions: facial={facial_prediction}, audio={audio_prediction}, text={text_prediction}")

        # Check if all predictions are available
        if not (facial_prediction and audio_prediction and text_prediction):
            logger.warning(f"Incomplete predictions for user {user.email if hasattr(user, 'email') else user.id}: facial={facial_prediction}, audio={audio_prediction}, text={text_prediction}")
            return Response({
                "message": "Incomplete predictions. Please provide all three predictions (facial, audio, text).",
                "received": {
                    "facial_prediction": facial_prediction,
                    "audio_prediction": audio_prediction,
                    "text_prediction": text_prediction
                },
                "debug": "Run missing endpoints: /api/sentiment/text/, /api/sentiment/audio/, or /api/emotion/detect-emotion/"
            }, status=status.HTTP_202_ACCEPTED)

        # Fusion logic: Majority vote
        prediction_list = [facial_prediction, audio_prediction, text_prediction]
        final_prediction = max(set(prediction_list), key=prediction_list.count)

        # Disorder → Test mapping
        disorder_tests = {
            "Depression": "Beck Depression Inventory (BDI)",
            "Anxiety": "Generalized Anxiety Disorder 7 (GAD-7)",
            "Overthinking": "Penn State Worry Questionnaire (PSWQ)",
            "Stress": "Perceived Stress Scale (PSS)",
            "Addiction": "Addiction Severity Index (ASI)",
            "OCD": "Yale-Brown Obsessive Compulsive Scale (Y-BOCS)",
            "Bipolar": "Mood Disorder Questionnaire (MDQ)",
            "PTSD": "Clinician-Administered PTSD Scale (CAPS-5)",
            "Eating Disorder": "Eating Disorder Examination Questionnaire (EDE-Q)",
            "Personality Disorder": "Minnesota Multiphasic Personality Inventory (MMPI-2-RF)",
            "Psychotic Disorder": "Brief Psychiatric Rating Scale (BPRS)",
            "Substance Use": "Drug Abuse Screening Test (DAST)",
            "ADHD": "Adult ADHD Self-Report Scale (ASRS)",
            "Sleep Disorder": "Pittsburgh Sleep Quality Index (PSQI)",
            "Impulse Control Disorder": "Barratt Impulsiveness Scale (BIS-11)"
        }

        # Map final prediction to disorder test
        disorder_test = disorder_tests.get(final_prediction, "No suitable test found")

        # Log the final prediction
        logger.debug(f"Final prediction for user {user.email if hasattr(user, 'email') else user.id}: {final_prediction}")

        # Save to FinalPrediction model
        final_prediction_obj, created = FinalPrediction.objects.get_or_create(
            user=user,
            defaults={
                'final_prediction': final_prediction,
                'disorder_test': disorder_test
            }
        )

        if not created:
            final_prediction_obj.final_prediction = final_prediction
            final_prediction_obj.disorder_test = disorder_test
            final_prediction_obj.save()

        # Return the final prediction with recommended disorder test
        return Response({
            "final_prediction": final_prediction,
            "disorder_test": disorder_test
        }, status=status.HTTP_200_OK)
