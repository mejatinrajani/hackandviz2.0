import torchaudio
import torch
from transformers import AutoFeatureExtractor, Wav2Vec2ForSequenceClassification
import torchaudio.transforms as T
from .audio_fusion import audio_fusion_logic  # Import fusion logic

# Load the model
model_name = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
extractor = AutoFeatureExtractor.from_pretrained(model_name)
model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)
label_mapping = model.config.id2label

def preprocess_audio(audio_file):
    """
    Preprocess the audio file: Convert to mono, apply noise reduction, and resample.
    """
    waveform, sample_rate = torchaudio.load(audio_file)

    # Convert stereo to mono if needed
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)

    # Resample to 16kHz if needed
    if sample_rate != 16000:
        resampler = T.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform)
    
    return waveform

def analyze_audio_sentiment(audio_file):
    """
    Analyze the sentiment from an audio file using the pre-trained Wav2Vec2 model.
    """
    try:
        # Preprocess the audio
        waveform = preprocess_audio(audio_file)
        
        # Feature extraction for the audio
        inputs = extractor(waveform.squeeze().numpy(), sampling_rate=16000, return_tensors="pt", padding=True)
        
        # Get emotion prediction
        with torch.no_grad():
            logits = model(**inputs).logits

        # Get the predicted class (emotion)
        pred_id = torch.argmax(logits).item()
        predicted_emotion = label_mapping[pred_id]
        
        # Confidence score (in this case, we use the maximum probability from the model's output logits)
        confidence = torch.nn.functional.softmax(logits, dim=-1).max().item()

        # Apply fusion logic to get disorder scores based on emotion and confidence
        disorder_scores_with_tests = audio_fusion_logic(predicted_emotion, confidence)

        return predicted_emotion, confidence, disorder_scores_with_tests

    except Exception as e:
        return str(e), None, None
