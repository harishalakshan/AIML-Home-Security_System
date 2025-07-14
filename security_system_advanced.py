import serial
import cv2
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from twilio.rest import Client
from sklearn.externals import joblib
import datetime
import os
import base64
from cryptography.fernet import Fernet

# === CONFIGURATION === #
# Load ML model
model = joblib.load('face_recognition_model.pkl')

# Encrypted Serial Key
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Serial connection (use /dev/ttyUSB0 for Raspberry Pi)
arduino = serial.Serial('/dev/ttyUSB0', 9600)

# Twilio configuration
twilio_sid = 'YOUR_TWILIO_SID'
twilio_token = 'YOUR_TWILIO_AUTH_TOKEN'
twilio_client = Client(twilio_sid, twilio_token)
twilio_from = '+1234567890'
twilio_to = '+0987654321'

# Email configuration
email_sender = 'you@example.com'
email_receiver = 'admin@example.com'
email_password = 'yourpassword'

# Haar cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# === FUNCTIONS === #
def send_sms_alert(message):
    twilio_client.messages.create(
        body=message,
        from_=twilio_from,
        to=twilio_to
    )

def send_email_alert(subject, body):
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ssl.create_default_context()) as server:
        server.login(email_sender, email_password)
        server.send_message(msg)

def log_to_cloud(event, img=None):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    os.makedirs('cloud_logs', exist_ok=True)
    if img is not None:
        cv2.imwrite(f'cloud_logs/{event}_{timestamp}.jpg', img)
    with open(f'cloud_logs/{event}_{timestamp}.txt', 'w') as f:
        f.write(f'{event} occurred at {timestamp}\n')

def capture_image():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam.release()
    return frame

def preprocess_image(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

def detect_faces(image):
    return face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5)

def extract_features(image, faces):
    features = []
    for (x, y, w, h) in faces:
        face = image[y:y+h, x:x+w]
        face_resized = cv2.resize(face, (100, 100)).flatten()
        features.append(face_resized)
    return features

def classify_faces(features):
    return [model.predict([f])[0] for f in features]

# === MAIN LOOP === #
while True:
    try:
        data = arduino.readline().decode().strip()
        decrypted_data = cipher_suite.decrypt(data.encode()).decode()

        if decrypted_data == 'MOTION_DETECTED':
            img = capture_image()
            gray = preprocess_image(img)
            faces = detect_faces(gray)

            if not faces.any():
                continue

            features = extract_features(gray, faces)
            labels = classify_faces(features)

            for label in labels:
                if label == 'INTRUDER':
                    print('[ALERT] Intruder detected!')
                    log_to_cloud('intruder', img)
                    send_sms_alert('Intruder alert at home!')
                    send_email_alert('Intruder Alert', 'An intruder has been detected by your smart security system.')
                    encrypted = cipher_suite.encrypt(b'ALARM_ON\n')
                    arduino.write(encrypted)
                elif label == 'AUTHORIZED':
                    print('[INFO] Authorized user.')
                    log_to_cloud('authorized')
                    encrypted = cipher_suite.encrypt(b'DOOR_OPEN\n')
                    arduino.write(encrypted)

    except Exception as e:
        print('[ERROR]', e)
