from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM
import torch
import torch.nn.functional as F

# Load models
goemotions_tokenizer = AutoTokenizer.from_pretrained("j-hartmann/emotion-english-distilroberta-base")
goemotions_model = AutoModelForSequenceClassification.from_pretrained("j-hartmann/emotion-english-distilroberta-base")

sentiment_tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
sentiment_model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")

mental_tokenizer = AutoTokenizer.from_pretrained("mental/mental-bert-base-uncased")
mental_model = AutoModelForSequenceClassification.from_pretrained("mental/mental-bert-base-uncased")

prompt_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
prompt_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")

# Labels
emotion_labels = goemotions_model.config.id2label
sentiment_labels = ['negative', 'neutral', 'positive']
mental_labels = mental_model.config.id2label

# Disorder mappings
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
    "Depression": "Beck Depression Inventory (BDI)",
    "Anxiety": "Generalized Anxiety Disorder 7 (GAD-7)",
    "Overthinking": "Penn State Worry Questionnaire (PSWQ)",
    "Stress": "Perceived Stress Scale (PSS)",
    "Addiction": "Addiction Severity Index (ASI)",
    "OCD": "Yale-Brown Obsessive Compulsive Scale (Y-BOCS)",
    "Bipolar": "Mood Disorder Questionnaire (MDQ)",
    "PTSD": "Clinician-Administered PTSD Scale (CAPS-5)",
    "Eating Disorder": "Eating Disorder Examination Questionnaire (EDE-Q)",
    "Personality Disorder": "Minnesota Multiphasic Personality Inventory (MMPI-2)",
    "Psychotic Disorder": "Brief Psychiatric Rating Scale (BPRS)",
    "Substance Use": "Drug Abuse Screening Test (DAST)",
    "ADHD": "Adult ADHD Self-Report Scale (ASRS)",
    "Sleep Disorder": "Pittsburgh Sleep Quality Index (PSQI)",
    "Impulse Control Disorder": "Barratt Impulsiveness Scale (BIS-11)"
}

# Final analysis function
def analyze_text(text):
    result = {}

    # --- Emotion Detection ---
    inputs = goemotions_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        logits = goemotions_model(**inputs).logits
        probs = torch.sigmoid(logits)[0]
    top_emotions = [emotion_labels[i.item()] for i in torch.topk(probs, 3).indices]
    result["emotions"] = top_emotions

    # --- Sentiment Detection ---
    inputs = sentiment_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        logits = sentiment_model(**inputs).logits
        probs = F.softmax(logits, dim=1)[0]
    sentiment = sentiment_labels[torch.argmax(probs).item()]
    result["sentiment"] = sentiment

    # --- MentalBERT Prediction ---
    inputs = mental_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        logits = mental_model(**inputs).logits
        probs = F.softmax(logits, dim=1)[0]
        pred = torch.argmax(probs).item()
    result["disorder_prediction"] = {
        "label": mental_labels[pred],
        "confidence": float(probs[pred])
    }

    # --- Prompt Reasoning ---
    prompt = f"Based on the user's description: {text}, what mental health disorders could they be suffering from?"
    inputs = prompt_tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = prompt_model.generate(inputs["input_ids"], max_new_tokens=30)
    generated_text = prompt_tokenizer.decode(outputs[0], skip_special_tokens=True)
    result["prompt_reasoning"] = generated_text

    # --- Fusion Logic ---
    disorder_score = {k: 0 for k in emotion_map.keys()}

    # Emotion signals
    for disorder, triggers in emotion_map.items():
        if any(e in triggers for e in top_emotions):
            disorder_score[disorder] += 1.0

    # Sentiment weighting
    if sentiment == "negative":
        for k in disorder_score:
            disorder_score[k] += 0.5

    # Model prediction
    predicted_disorder = result["disorder_prediction"]["label"]
    if predicted_disorder in disorder_score:
        disorder_score[predicted_disorder] += 2.0

    # Prompt matching (soft match)
    for disorder in disorder_score:
        if disorder.lower() in generated_text.lower():
            disorder_score[disorder] += 1.5

    # Select final disorders
    sorted_disorders = sorted(disorder_score.items(), key=lambda x: x[1], reverse=True)
    final_disorders = [d for d, score in sorted_disorders if score >= 1.5][:3]

    result["final_disorders"] = final_disorders
    result["disorder_score"] = disorder_score
    result["suggested_tests"] = {d: disorder_tests[d] for d in final_disorders if d in disorder_tests}

    return result
