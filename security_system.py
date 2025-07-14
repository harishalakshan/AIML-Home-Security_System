import serial
import cv2
import numpy as np
from sklearn.externals import joblib  # If deprecated, use: from joblib import load

# Load pre-trained face recognition model
model = joblib.load('face_recognition_model.pkl')  # Your trained model file

# Open Serial connection to Arduino (update COM port as needed)
arduino = serial.Serial('COM3', 9600)  # Replace 'COM3' with your actual port

# Load Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Function to capture an image from webcam
def capture_image():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam.release()
    return frame

# Preprocess captured frame
def preprocess_image(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray

# Detect faces in image
def detect_faces(image):
    return face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5)

# Extract and flatten face regions
def extract_features(image, faces):
    features = []
    for (x, y, w, h) in faces:
        face = image[y:y+h, x:x+w]
        face_resized = cv2.resize(face, (100, 100))  # Resize to model input shape
        features.append(face_resized.flatten())      # Flatten image to 1D array
    return features

# Predict labels using ML model
def classify_faces(features):
    results = []
    for face in features:
        label = model.predict([face])[0]  # Predict label
        results.append(label)
    return results

# Main loop
while True:
    try:
        data = arduino.readline().decode().strip()  # Read serial data

        if data == 'MOTION_DETECTED':
            print("[INFO] Motion detected. Capturing image...")
            frame = capture_image()
            processed = preprocess_image(frame)
            faces = detect_faces(processed)

            if len(faces) == 0:
                print("[INFO] No face detected.")
                continue

            features = extract_features(processed, faces)
            labels = classify_faces(features)

            for label in labels:
                if label == 'INTRUDER':
                    print("[ALERT] Intruder detected!")
                    arduino.write(b'ALARM_ON\n')
                elif label == 'AUTHORIZED':
                    print("[INFO] Authorized person detected.")
                    arduino.write(b'DOOR_OPEN\n')
                else:
                    print("[WARNING] Unknown face detected.")

    except Exception as e:
        print("[ERROR]", e)
