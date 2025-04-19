import cv2
import gc
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from deepface import DeepFace
import numpy as np
from collections import Counter
import psutil
import os
import logging
from final_prediction.models import UserPrediction

# Set up logging
logger = logging.getLogger(__name__)

# Emotion to Disorder mapping
emotion_map = {
    "Depression": ["sadness", "grief", "disappointment", "hopelessness"],
    "Anxiety": ["fear", "nervousness", "embarrassment", "apprehension"],
    "Overthinking": ["confusion", "overwhelm", "uncertainty"],
    "Stress": ["annoyance", "frustration", "irritability", "exhaustion"],
    "Addiction": ["desire", "obsession", "compulsion"],
    "OCD": ["intrusive thoughts", "repetitiveness", "compulsion"],
    "Bipolar": ["mania", "elation", "euphoria", "depression"],
    "PTSD": ["hypervigilance", "flashbacks", "fear", "avoidance"],
    "Eating Disorder": ["guilt", "shame", "fear of food", "control"],
    "Personality Disorder": ["manipulation", "impulsivity", "mood swings"],
    "Psychotic Disorder": ["delusions", "paranoia", "hallucinations"],
    "Substance Use": ["dependency", "craving", "desire", "addiction"],
    "ADHD": ["impulsivity", "restlessness", "inattention", "distraction"],
    "Sleep Disorder": ["insomnia", "fatigue", "restlessness", "drowsiness"],
    "Impulse Control Disorder": ["compulsion", "gambling", "stealing", "fidgeting"]
}

disorder_tests = {
    "Depression": "Beck Depression Inventory (BDI-II)",
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

class DetectEmotionAndPredictDisorderView(APIView):
    def post(self, request):
        # Clear memory at the start
        logger.debug("Attempting to clear memory before processing")
        gc.collect()  # Force garbage collection
        # Release any existing OpenCV resources
        if 'cap' in locals():
            del cap
            cv2.destroyAllWindows()
        # Clear system cache if possible (platform-dependent)
        try:
            if os.name == 'nt':  # Windows
                os.system('echo y|del /F /Q %temp%\\*.*')
            elif os.name == 'posix':  # Linux/Unix
                os.system('sync; echo 3 > /proc/sys/vm/drop_caches')
        except Exception as e:
            logger.warning(f"Failed to clear system cache: {str(e)}")

        memory_percent = psutil.virtual_memory().percent
        logger.debug(f"Memory usage after cleanup: {memory_percent}%")
        if memory_percent > 80:
            logger.error("Memory limit exceeded even after cleanup")
            return Response({"error": "System memory limit exceeded. Please free up memory or use a shorter video."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.debug(f"Request files: {request.FILES}")
        video_file = request.FILES.get("video")
        if not video_file:
            logger.error("Video file missing in request")
            return Response({"error": "Video file is required. Ensure the key is 'video'."}, status=status.HTTP_400_BAD_REQUEST)

        video_path = os.path.join('media', 'videos', 'uploaded_video.mp4')
        os.makedirs(os.path.dirname(video_path), exist_ok=True)

        try:
            with open(video_path, 'wb') as f:
                for chunk in video_file.chunks():
                    f.write(chunk)
        except Exception as e:
            logger.error(f"Error saving video: {str(e)}")
            return Response({"error": f"Failed to save video: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error("Failed to open video")
                return Response({"error": "Failed to open video. Ensure it’s a valid MP4 file."}, status=status.HTTP_400_BAD_REQUEST)

            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
            duration = frame_count / frame_rate if frame_rate > 0 else 0
            if duration > 300:  # 5-minute limit
                cap.release()
                logger.error("Video duration exceeds 5 minutes")
                return Response({"error": "Video exceeds 5 minutes. Please upload a shorter video."}, status=status.HTTP_400_BAD_REQUEST)

            # Dynamic frame sampling based on memory and duration
            target_frames = min(50, frame_count)  # Reduced to 50 frames to minimize memory
            frame_skip = max(1, frame_count // target_frames) if frame_count > target_frames else 1
            max_frames = target_frames
            logger.debug(f"Video duration: {duration}s, Frame count: {frame_count}, Frame skip: {frame_skip}")

            frame_count = 0
            emotions_per_frame = []
            no_face_frames = 0

            while cap.isOpened() and frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_skip == 0:
                    # Downscale dynamically based on memory
                    memory_percent = psutil.virtual_memory().percent
                    scale_factor = 0.25 if memory_percent > 75 else 0.5  # More aggressive downscaling
                    frame = cv2.resize(frame, (int(120 * scale_factor), int(90 * scale_factor)))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    if memory_percent > 90:
                        logger.error(f"Memory critical at frame {frame_count}: {memory_percent}%")
                        cap.release()
                        return Response({"error": "Memory limit exceeded during processing. Try a shorter video or free up memory."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    try:
                        # Reduced contrast enhancement for lower processing load
                        frame = cv2.convertScaleAbs(frame, alpha=1.1, beta=5)
                        result = DeepFace.analyze(
                            frame,
                            actions=['emotion'],
                            enforce_detection=False,
                            detector_backend='retinaface',
                            silent=True
                        )
                        if isinstance(result, list) and result:
                            emotions = result[0]['emotion']
                            dominant_emotion = max(emotions, key=emotions.get)
                            emotions_per_frame.append(dominant_emotion)
                            logger.debug(f"Frame {frame_count}: Detected emotion {dominant_emotion}")
                        else:
                            no_face_frames += 1
                            logger.debug(f"Frame {frame_count}: No face detected")
                    except Exception as e:
                        logger.debug(f"Frame {frame_count}: Error - {str(e)}")
                        if "face" in str(e).lower():
                            no_face_frames += 1
                        else:
                            logger.error(f"Non-face error: {str(e)}")

                    # Immediate cleanup
                    del frame
                    gc.collect()

                frame_count += 1

            cap.release()

            # Fallback if no emotions detected
            if not emotions_per_frame:
                logger.warning(f"No emotions detected. Processed {frame_count} frames, {no_face_frames} had no faces.")
                facial_prediction = "No significant disorder"
                disorder_scores = []
            else:
                fused_emotions = self.enhance_fuse_emotions(emotions_per_frame)
                disorder_scores = self.predict_disorders(fused_emotions)
                facial_prediction = max(disorder_scores, key=lambda x: x['score'])['disorder'] if disorder_scores else "No significant disorder"

            # Save to UserPrediction
            user = request.user
            if user.is_authenticated:
                try:
                    user_prediction, created = UserPrediction.objects.get_or_create(
                        user=user,
                        defaults={
                            'video_emotion': facial_prediction,
                            'video_confidence': 0.7,
                            'video_disorders': disorder_scores
                        }
                    )
                    if not created:
                        user_prediction.video_emotion = facial_prediction
                        user_prediction.video_confidence = 0.7
                        user_prediction.video_disorders = disorder_scores
                        user_prediction.save()
                    logger.debug(f"Saved facial prediction for user {user.email if hasattr(user, 'email') else user.id}: {facial_prediction}")
                except Exception as e:
                    logger.error(f"Error saving UserPrediction: {str(e)}")
            else:
                logger.warning("User not authenticated. Skipping UserPrediction save.")

            return Response({
                "dominant_emotion": fused_emotions if emotions_per_frame else None,
                "emotion_confidences": dict(Counter(emotions_per_frame)) if emotions_per_frame else {},
                "predicted_disorders": disorder_scores,
                "frames_processed": frame_count,
                "no_face_frames": no_face_frames,
                "facial_prediction": facial_prediction
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            try:
                if os.path.exists(video_path):
                    os.remove(video_path)
                    logger.debug("Temporary video file removed")
            except Exception as e:
                logger.error(f"Error removing video file: {str(e)}")
            if 'cap' in locals():
                cap.release()
                cv2.destroyAllWindows()
                gc.collect()

    def enhance_fuse_emotions(self, emotions_per_frame):
        emotion_counter = Counter(emotions_per_frame)
        return emotion_counter.most_common(1)[0][0]

    def predict_disorders(self, dominant_emotion):
        disorder_scores = []
        for disorder, emotions in emotion_map.items():
            if dominant_emotion in emotions:
                disorder_scores.append({
                    "disorder": disorder,
                    "score": 70.0,
                    "test_recommendation": disorder_tests.get(disorder)
                })
        return disorder_scores