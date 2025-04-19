from transformers import pipeline

def detect_mood(text):
    classifier = pipeline(
        "text-classification",
        model="bhadresh-savani/distilbert-base-uncased-emotion"
    )
    result = classifier(text)[0]
    return result['label'].lower()  # joy/sadness/anger/love/surprise/fear