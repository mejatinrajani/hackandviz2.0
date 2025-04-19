from rest_framework.views import APIView
from rest_framework.response import Response as DRFResponse
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from .models import Test, Question, ClinicalSession, Response as ResponseModel
from .serializers import TestSerializer, ClinicalSessionSerializer, QuestionSerializer
from .utils import generate_clinical_report_pdf
from final_prediction.models import FinalPrediction
import re
import os
try:
    import google.generativeai as genai
except ImportError:
    genai = None

def call_gemini_api(prompt):
    """Call Gemini API for follow-up questions."""
    if not genai:
        return ["Gemini API not available. Install google-generativeai."]
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY', 'your-gemini-api-key'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        questions = response.text.strip().split('\n')[:3]
        return [q for q in questions if q]
    except Exception as e:
        return [f"Error generating follow-up questions: {str(e)}"]


def is_response_unclear(question, selected_option, open_ended_answer):
    """Determine if a response needs follow-up questions."""
    if question.is_open_ended:
        if not open_ended_answer or len(open_ended_answer.split()) < 10 or open_ended_answer.lower() in ["i don't know", "not sure"]:
            return True
        return False
    if not selected_option:
        return True
    unclear_options = [
        "Sometimes", "Several days", "More than half the days",
        "Neutral", "Somewhat typical", "Somewhat not typical",
        "Occasionally", "Often", "Mild", "Moderate"
    ]
    return selected_option['text'] in unclear_options

def get_follow_up_questions(question_text, response_text):
    """Generate follow-up questions using Gemini."""
    prompt = f"""
You are an informational assistant providing educational support. A user responded to the following question with the answer below. The response is unclear or vague. Generate 1–3 open-ended follow-up questions to clarify their experience without offering medical advice or diagnoses. Use a neutral, professional tone.

Question: {question_text.splitlines()[0]}
Response: {response_text}

Example follow-up questions:
- Can you describe what you mean by your response?
- How often does this affect your daily activities?
- What specific situations make you feel this way?

Follow-up questions:
"""
    return call_gemini_api(prompt)

def calculate_score(responses, scoring_rules, test_name):
    """Calculate total score and severity."""
    total = 0
    severity = "Unknown"

    if "BDI-II" in test_name:
        total = sum(r.selected_option['score'] for r in responses if r.selected_option)
        if total <= 13:
            severity = "Minimal"
        elif total <= 19:
            severity = "Mild"
        elif total <= 28:
            severity = "Moderate"
        else:
            severity = "Severe"
    elif "GAD-7" in test_name:
        total = sum(r.selected_option['score'] for r in responses if r.selected_option)
        if total <= 4:
            severity = "Minimal"
        elif total <= 9:
            severity = "Mild"
        elif total <= 14:
            severity = "Moderate"
        else:
            severity = "Severe"
    elif "PSWQ" in test_name:
        for idx, r in enumerate(responses, 1):
            if not r.selected_option:
                continue
            score = r.selected_option['score']
            if idx in [1, 3, 8, 10, 11]:
                score = 6 - score
            total += score
        severity = "High Worry" if total >= 50 else "Low Worry"
    elif "PSS-10" in test_name:
        for idx, r in enumerate(responses, 1):
            if not r.selected_option:
                continue
            score = r.selected_option['score']
            if idx in [4, 5, 7, 8]:
                score = 4 - score
            total += score
        if total <= 13:
            severity = "Low"
        elif total <= 26:
            severity = "Moderate"
        else:
            severity = "High"
    elif "Y-BOCS" in test_name:
        total = sum(r.selected_option['score'] for r in responses if r.selected_option)
        if total <= 7:
            severity = "Subclinical"
        elif total <= 15:
            severity = "Mild"
        elif total <= 23:
            severity = "Moderate"
        elif total <= 31:
            severity = "Severe"
        else:
            severity = "Extreme"
    elif "MDQ" in test_name:
        q1_count = sum(1 for r in responses[:13] if r.selected_option and r.selected_option['score'] == 1)
        q2_yes = responses[13].selected_option['score'] == 1 if len(responses) > 13 else False
        q3_level = responses[14].selected_option['text'] if len(responses) > 14 else "None"
        total = q1_count
        if q1_count >= 7 and q2_yes and q3_level in ["Moderate", "Serious"]:
            severity = "Positive Screen"
        else:
            severity = "Negative Screen"
    elif "ASI" in test_name:
        total = sum(r.selected_option['score'] for r in responses if r.selected_option and r.question.order in [2, 3, 6, 9, 12, 14])
        severity = "Placeholder: ASI requires composite scoring per domain"
    elif "BPRS" in test_name:
        total = sum(r.selected_option['score'] for r in responses if r.selected_option)
        if total <= 30:
            severity = "Minimal"
        elif total <= 40:
            severity = "Mild"
        elif total <= 52:
            severity = "Moderate"
        else:
            severity = "Severe"
    elif "DAST-10" in test_name:
        total = sum(r.selected_option['score'] for r in responses if r.selected_option)
        if total <= 2:
            severity = "Low"
        elif total <= 5:
            severity = "Moderate"
        elif total <= 8:
            severity = "Substantial"
        else:
            severity = "Severe"
    elif "ASRS" in test_name:
        total = sum(r.selected_option['score'] for r in responses if r.selected_option)
        severity = "ADHD Likely" if total >= 14 else "ADHD Unlikely"
    elif "PSQI" in test_name:
        components = [0] * 7
        for idx, r in enumerate(responses, 1):
            if r.selected_option:
                components[idx-1] = r.selected_option['score']
        total = sum(components)
        severity = "Poor Sleep" if total >= 5 else "Good Sleep"
    elif "BIS-11" in test_name:
        for idx, r in enumerate(responses, 1):
            if not r.selected_option:
                continue
            score = r.selected_option['score']
            if idx in [1, 8, 10]:
                score = 5 - score
            total += score
        severity = "High Impulsivity" if total >= 20 else "Average"
    elif "CAPS-5" in test_name:
        total = sum(r.selected_option['score'] for r in responses if r.selected_option)
        if total <= 19:
            severity = "Subclinical"
        elif total <= 39:
            severity = "Mild"
        elif total <= 59:
            severity = "Moderate"
        else:
            severity = "Severe"
    elif "EDE-Q" in test_name:
        total = sum(r.selected_option['score'] for r in responses if r.selected_option) / 10
        severity = "Clinical Concern" if total >= 4 else "Normal"
    elif "MMPI-2-RF" in test_name:
        total = sum(1 for r in responses if r.selected_option and r.selected_option['text'] == "True")
        severity = "Placeholder: MMPI-2-RF requires professional scoring"
    elif "General Psychological Screening" in test_name:
        total = sum(r.selected_option['score'] for r in responses if r.selected_option)
        if total <= 5:
            severity = "Low"
        elif total <= 10:
            severity = "Moderate"
        else:
            severity = "High"
        severity += " (Placeholder: Consult professional)"
    else:
        total = sum(r.selected_option['score'] for r in responses if r.selected_option)
        severity = "Placeholder: Contact copyright holder"

    return total, severity

class ListTests(APIView):
    def get(self, request):
        tests = Test.objects.all()
        serializer = TestSerializer(tests, many=True)
        return DRFResponse(serializer.data)

import logging
logger = logging.getLogger(__name__)

import logging
logger = logging.getLogger(__name__)

class StartClinicalTestFromPrediction(APIView):
    def post(self, request):
        logger.debug(f"Received request: {request.data}")
        prediction_id = request.data.get('prediction_id')
        logger.debug(f"Fetching FinalPrediction with id={prediction_id}")
        prediction = get_object_or_404(FinalPrediction, id=prediction_id, user=request.user)
        
        test_name_mapping = {
            "Beck Depression Inventory (BDI)": "Beck Depression Inventory (BDI-II)",
            "Generalized Anxiety Disorder 7 (GAD-7)": "Generalized Anxiety Disorder 7 (GAD-7)",
            "Penn State Worry Questionnaire (PSWQ)": "Penn State Worry Questionnaire (PSWQ)",
            "Perceived Stress Scale (PSS)": "Perceived Stress Scale (PSS-10)",
            "Yale-Brown Obsessive Compulsive Scale (Y-BOCS)": "Yale-Brown Obsessive Compulsive Scale (Y-BOCS)",
            "Mood Disorder Questionnaire (MDQ)": "Mood Disorder Questionnaire (MDQ)",
            "Addiction Severity Index (ASI)": "Addiction Severity Index (ASI)",
            "Brief Psychiatric Rating Scale (BPRS)": "Brief Psychiatric Rating Scale (BPRS)",
            "Drug Abuse Screening Test (DAST)": "Drug Abuse Screening Test (DAST-10)",
            "Adult ADHD Self-Report Scale (ASRS)": "Adult ADHD Self-Report Scale (ASRS-v1.1)",
            "Pittsburgh Sleep Quality Index (PSQI)": "Pittsburgh Sleep Quality Index (PSQI)",
            "Barratt Impulsiveness Scale (BIS-11)": "Barratt Impulsiveness Scale (BIS-11)",
            "Clinician-Administered PTSD Scale (CAPS-5)": "Clinician-Administered PTSD Scale (CAPS-5)",
            "Eating Disorder Examination Questionnaire (EDE-Q)": "Eating Disorder Examination Questionnaire (EDE-Q 6.0)",
            "Minnesota Multiphasic Personality Inventory (MMPI-2)": "Minnesota Multiphasic Personality Inventory (MMPI-2-RF)"
        }
        test_name = test_name_mapping.get(prediction.recommended_tests, prediction.recommended_tests)
        logger.debug(f"Looking for Test with name={test_name}")
        logger.debug(f"Available tests: {[t.name for t in Test.objects.all()]}")
        
        test = get_object_or_404(Test, name=test_name)
        logger.debug(f"Found Test: {test.name}, is_placeholder={test.is_placeholder}")
        if test.is_placeholder:
            logger.debug(f"Returning placeholder warning for test_id={test.id}")
            return DRFResponse({
                "warning": "This test contains placeholder questions. Official questions require copyright permission.",
                "test_id": test.id
            }, status=status.HTTP_200_OK)
        session = ClinicalSession.objects.create(
            user=request.user,
            test=test,
            prediction=prediction
        )
        first_question = test.questions.first()
        if not first_question:
            logger.debug(f"No questions available for test {test.name}")
            return DRFResponse({"error": "No questions available"}, status=status.HTTP400_BAD_REQUEST)
        logger.debug(f"Created ClinicalSession id={session.id}, returning first question")
        return DRFResponse({
            "session_id": session.id,
            "disorder": prediction.final_prediction,
            "question": QuestionSerializer(first_question).data
        })
    

class ContinueClinicalTest(APIView):
    def post(self, request):
        session_id = request.data.get('session_id')
        question_id = request.data.get('question_id')
        selected_option = request.data.get('selected_option')
        open_ended_answer = request.data.get('open_ended_answer')

        session = get_object_or_404(ClinicalSession, id=session_id, user=request.user)
        question = get_object_or_404(Question, id=question_id, test=session.test)

        # Validate response
        if question.is_open_ended and not open_ended_answer:
            return DRFResponse({"error": "Open-ended answer required"}, status=status.HTTP_400_BAD_REQUEST)
        if not question.is_open_ended and selected_option:
            # Ensure options is a list; handle potential malformed data
            options = question.options if isinstance(question.options, list) else []
            if not any(isinstance(opt, dict) and opt.get('text') == selected_option.get('text') and opt.get('score') == selected_option.get('score') for opt in options):
                return DRFResponse({"error": "Invalid option selected"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if follow-up is needed
        follow_up_questions = []
        response_text = open_ended_answer if question.is_open_ended else (selected_option.get('text') if selected_option else "")
        if is_response_unclear(question, selected_option, open_ended_answer):
            follow_up_questions = get_follow_up_questions(question.text, response_text)

        # Save response
        response = ResponseModel.objects.create(
            session=session,
            question=question,
            selected_option=selected_option,
            open_ended_answer=open_ended_answer,
            follow_up_questions=follow_up_questions if follow_up_questions else None
        )

        # Get next question
        next_question = session.test.questions.filter(order__gt=question.order).first()
        if next_question:
            return DRFResponse({
                "session_id": session.id,
                "disorder": session.prediction.final_prediction if session.prediction else "Unknown",
                "question": QuestionSerializer(next_question).data,
                "previous_response_follow_ups": follow_up_questions
            })

        # Test complete
        session.is_complete = True
        responses = session.responses.all()
        total_score, severity = calculate_score(responses, session.test.scoring_rules, session.test.name)
        session.total_score = total_score
        session.severity = severity
        session.completed_at = timezone.now()
        session.save()

        return DRFResponse({
            "session_id": session.id,
            "disorder": session.prediction.final_prediction if session.prediction else "Unknown",
            "is_complete": True,
            "total_score": total_score,
            "severity": severity,
            "disclaimer": "This is not a diagnosis. Consult a licensed mental health professional for an accurate assessment."
        })

class DownloadReport(APIView):
    def get(self, request, session_id):
        session = get_object_or_404(ClinicalSession, id=session_id, user=request.user)
        pdf_buffer = generate_clinical_report_pdf(session)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="clinical_report_{session_id}.pdf"'
        return response