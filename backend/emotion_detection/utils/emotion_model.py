import numpy as np
from keras.models import load_model
from .preprocess import preprocess_image

# Load model once when server starts
model = load_model('emotion_detection/model/model_v6_23.hdf5')  # Path to your emotion model

emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

def predict_emotion(face_image):
    img_array = preprocess_image(face_image)  # Preprocess the image for model
    prediction = model.predict(img_array)      # Get model's prediction
    emotion = emotion_labels[np.argmax(prediction)]  # Get the emotion with highest probability
    return emotion
