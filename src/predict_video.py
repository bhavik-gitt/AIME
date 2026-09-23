import os
import cv2
import numpy as np
import tensorflow as tf

# ================= CONFIG =================
MODEL_PATH = r"..\models\video_emotion_model.h5"
VIDEO_PATH = r"C:\Btech It Sem 6\PROJECT\dataset\RAVDESS dataset\Video_Speech_Actor_01\Actor_01\01-01-01-01-01-01-01.mp4"
IMG_SIZE = 160
FPS_SKIP = 2          # LOWER = better detection
# =========================================

emotion_labels = [
    "neutral", "calm", "happy", "sad",
    "angry", "fear", "disgust", "surprise"
]

print("🔄 Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)
print("✅ Model loaded\n")

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

cap = cv2.VideoCapture(VIDEO_PATH)

predictions = []
frame_count = 0
faces_seen = 0

print("🎥 Processing video for prediction...\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % FPS_SKIP != 0:
        continue

    frame = cv2.resize(frame, (640, 480))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,    # MORE sensitive
        minNeighbors=3,     # LESS strict
        minSize=(60, 60)
    )

    for (x, y, w, h) in faces:
        faces_seen += 1
        face = frame[y:y+h, x:x+w]
        if face.size == 0:
            continue

        face = cv2.resize(face, (IMG_SIZE, IMG_SIZE))
        face = face.astype("float32") / 255.0
        face = np.expand_dims(face, axis=0)

        pred = model.predict(face, verbose=0)[0]
        predictions.append(pred)
        break   # one face per frame

cap.release()

# ================= RESULT =================
if len(predictions) == 0:
    print("❌ No face detected in the video.")
    print("📌 Tips:")
    print("- Use a frontal face video")
    print("- Ensure good lighting")
    print("- Face should occupy good portion of frame")
    print("- Avoid sunglasses / masks")
    exit()

predictions = np.array(predictions)
avg_prediction = np.mean(predictions, axis=0)

emotion_index = np.argmax(avg_prediction)
emotion = emotion_labels[emotion_index]
confidence = avg_prediction[emotion_index]

print("🎯 FINAL PREDICTION")
print("-" * 30)
print(f"Emotion      : {emotion}")
print(f"Confidence   : {confidence * 100:.2f}%")
print(f"Frames used  : {len(predictions)}")
print(f"Faces seen   : {faces_seen}")
