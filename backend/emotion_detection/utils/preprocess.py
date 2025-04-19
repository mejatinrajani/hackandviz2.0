import cv2
import numpy as np
from PIL import Image
import io

def preprocess_image(image_bytes):
    # Convert the face image to grayscale and resize it to 48x48 (expected by your model)
    img = cv2.cvtColor(image_bytes, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    img = cv2.resize(img, (48, 48))  # Resize image to 48x48
    img_array = np.array(img)
    img_array = img_array.astype('float32') / 255.0  # Normalize the image
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array = np.expand_dims(img_array, axis=-1)  # Add channel dimension (1 channel for grayscale)
    return img_array
