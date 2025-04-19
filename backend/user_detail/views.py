from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserResponse
from .questions import questions
from .conversation_engine import chatbot
from .followup_user import FOLLOWUP_RULES  # ✅ Import rule-based followups

MAX_FOLLOWUPS = 4  # ✅ Limit total follow-ups to 4


def handle_next_question(user):
    past_responses = UserResponse.objects.filter(user=user)

    if not past_responses.exists():
        intro_prompt = (
            "You are AuroraMinds, a friendly mental health companion. Greet the user warmly and let them know "
            "you’ll be asking a few short questions about their daily lifestyle, like name, age, work, family, "
            "and general mental health. Emphasize that this is not a test, just a quick 2-minute form to better understand them. "
            "Let them know you're here for support and no matter what they share, MindSync and its therapists are here to help."
        )
        message = chatbot.generate_response(intro_prompt)
        return {"type": "intro", "message": message}

    answered_questions = [resp.question for resp in past_responses if not resp.is_followup]
    remaining_questions = [q for q in questions if q["question"] not in answered_questions]

    if remaining_questions:
        return {"type": "question", "question": remaining_questions[0]}

    return {"type": "end", "message": "Thanks for completing the form! You're awesome and we're glad to have you here 😊"}


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def start_conversation(request):
    user = request.user
    return Response(handle_next_question(user))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_answer(request):
    user = request.user
    question = request.data.get("question")
    answer = request.data.get("answer")

    if not question or not answer:
        return Response({"error": "Question and answer are required."}, status=400)

    # Save user response
    UserResponse.objects.create(user=user, question=question, response=answer)

    # Count followups so far
    followup_count = UserResponse.objects.filter(user=user, is_followup=True).count()
    if followup_count >= MAX_FOLLOWUPS:
        return Response(handle_next_question(user))

    # --- Step 1: Check emotion-based relaxing messages
    relaxation_prompts = {
        "stressed": "Don't worry, MindSync and its therapists are with you. You don't need to worry — just stick with the form, we're here to support you every step of the way!",
        "anxious": "We understand, but take a deep breath! MindSync and its team are here to guide you through, and there’s no rush. You're doing great!",
        "low": "It's okay to feel down sometimes. We're here to listen, and you’re not alone. Let’s take it one step at a time — you're doing wonderfully!",
        "worried": "It's totally okay to feel worried. MindSync and our therapists are with you. Just take it slow and continue with the form — you've got this!"
    }

    negative_emotions = ["stressed", "anxious", "low", "worried"]
    for emotion in negative_emotions:
        if emotion in answer.lower():
            return Response({
                "type": "followup",
                "question": relaxation_prompts[emotion]
            })

    # --- Step 2: Rule-based followups
    if question in FOLLOWUP_RULES:
        possible_answers = [a.strip().lower() for a in answer.split(",")]

        for user_answer in possible_answers:
            for option_key in FOLLOWUP_RULES[question]:
                if user_answer in option_key.lower():
                    followup_list = FOLLOWUP_RULES[question][option_key]
                    asked_followups = UserResponse.objects.filter(user=user, is_followup=True).values_list('question', flat=True)
                    next_followup = next((f for f in followup_list if f not in asked_followups), None)

                    if next_followup and followup_count < MAX_FOLLOWUPS:
                        return Response({
                            "type": "followup",
                            "question": next_followup
                        })

    # --- Step 3: Fallback to Gemini for general clarification
    if followup_count < MAX_FOLLOWUPS:
        context_history = "\n".join(
            f"{resp.question}: {resp.response}" for resp in UserResponse.objects.filter(user=user)
        )
        followup_prompt = (
            f"You are MindSync, a gentle and intelligent mental health assistant. The user said: '{answer}' in response to: '{question}'. "
            f"Your goal is to collect basic but meaningful user information — such as their name, age, work situation, family background, lifestyle habits, and a rough sense of their current mental state. "
            f"This is an onboarding form — not a diagnostic session — but you may ask one brief and slightly clinical follow-up if it helps understand them better. "
            f"If no follow-up is necessary, respond with 'No follow-up needed'. "
            f"Make sure the follow-up is supportive, empathetic, and relevant to the user's response. Do not repeat previously asked questions."
        )

        followup = chatbot.generate_response(followup_prompt)

        if followup and "no follow-up" not in followup.lower():
            return Response({
                "type": "followup",
                "question": followup
            })

    # --- Step 4: Move on to next main question
    return Response(handle_next_question(user))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_followup(request):
    user = request.user
    question = request.data.get("question")
    answer = request.data.get("answer")

    if not question or not answer:
        return Response({"error": "Follow-up question and answer are required."}, status=400)

    # Save follow-up
    UserResponse.objects.create(
        user=user,
        question=question,
        response=answer,
        is_followup=True
    )

    # Return next main question or finish
    return Response(handle_next_question(user))
