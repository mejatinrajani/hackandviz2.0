# emotion-to-disorder mapping based on audio prediction
AUDIO_DISORDER_MAPPING = {
    'happy': {
        'depression': 0.1, 'stress': 0.1, 'no_significant_disorder': 0.8
    },
    'sad': {
        'depression': 0.8, 'stress': 0.1, 'anxiety': 0.1
    },
    'angry': {
        'anxiety': 0.6, 'stress': 0.3, 'overthinking': 0.1
    },
    'neutral': {
        'no_significant_disorder': 0.9, 'stress': 0.1
    },
    'fearful': {
        'anxiety': 0.8, 'stress': 0.15, 'overthinking': 0.05
    },
    'surprised': {
        'no_significant_disorder': 0.9, 'stress': 0.1
    }
    # Add other emotions as needed
}

# Disorder-to-test mapping
DISORDER_TESTS = {
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

def audio_fusion_logic(audio_emotion, confidence, threshold=0.5):
    """
    Apply dynamic fusion logic based on predicted emotion from audio and confidence level.
    This function allows for dynamic weighting of disorders based on confidence.
    """
    disorder_scores = AUDIO_DISORDER_MAPPING.get(audio_emotion.lower(), {})
    
    # Adjust the disorder scores based on the confidence
    adjusted_scores = {}

    for disorder, weight in disorder_scores.items():
        # If confidence is higher than threshold, boost the weight for the disorder
        if confidence >= threshold:
            adjusted_scores[disorder] = round(weight * confidence, 2)
        else:
            adjusted_scores[disorder] = round(weight * 0.5, 2)  # Lower weight if confidence is low

    # Get disorders with their corresponding tests
    disorder_with_tests = {}
    for disorder in adjusted_scores.keys():
        disorder_with_tests[disorder] = {
            "score": adjusted_scores[disorder],
            "test": DISORDER_TESTS.get(disorder, "No specific test available")
        }

    return disorder_with_tests
