from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .utils.mood import detect_mood
from .utils.recommender import hybrid_recommend

@csrf_exempt
def recommend(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_text = data.get("text", "").strip()
            
            if not user_text:
                return JsonResponse({"error": "No input provided"}, status=400)
            
            mood = detect_mood(user_text)
            results = hybrid_recommend(mood)
            
            return JsonResponse(results)
            
        except Exception as e:
            return JsonResponse({
                "error": str(e),
                "solution": "Check server logs for details"
            }, status=500)
    
    return JsonResponse({"error": "POST method required"}, status=405)