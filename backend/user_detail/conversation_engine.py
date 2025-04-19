# conversation_engine.py
from .models import UserResponse
from .gemini_service import GeminiChatBot  # Correct class name

chatbot = GeminiChatBot()



DEFAULT_SYSTEM_PROMPT = (
    "You are a friendly and professional mental health assistant. "
    "Ask the user one personal or mental health-related question at a time. "
    "Start by introducing yourself. Stop when you have enough information."
)

def get_next_question(user, user_reply=None):
    convo, created = UserResponse.objects.get_or_create(user=user, is_complete=False)

    if convo.history.strip() == "":
        convo.history = DEFAULT_SYSTEM_PROMPT + "\n"

    if user_reply:
        convo.history += f"User: {user_reply}\n"

    prompt = convo.history + "AI:"
    ai_response = chatbot.generate(prompt)

    if any(kw in ai_response.lower() for kw in ["thank you", "all the info", "that's all"]):
        convo.is_complete = True

    convo.history += f"AI: {ai_response}\n"
    convo.save()

    return ai_response, convo.is_complete
