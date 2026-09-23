import os
import cv2
import numpy as np
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model

# ================= CONFIG =================
DATASET_PATH = r"C:\Btech It Sem 6\PROJECT\dataset\RAVDESS dataset"

IMG_SIZE = 160          # MEMORY SAFE
FPS_SKIP = 10
MAX_FRAMES = 20
MAX_VIDEOS = 300        # LIMIT FOR FAST TRAINING

EPOCHS = 12
BATCH_SIZE = 32
# =========================================

emotion_map = {
    "01": 0, "02": 1, "03": 2, "04": 3,
    "05": 4, "06": 5, "07": 6, "08": 7
}

# OpenCV Haar Cascade
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

X, labels = [], []

def extract_faces(video_path, emotion):
    cap = cv2.VideoCapture(video_path)
    frame_count, faces_used = 0, 0

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
            gray, scaleFactor=1.2, minNeighbors=5
        )

        for (x, y, w, h) in faces:
            face = frame[y:y+h, x:x+w]
            if face.size == 0:
                continue

            face = cv2.resize(face, (IMG_SIZE, IMG_SIZE))
            X.append(face)
            labels.append(emotion_map[emotion])

            faces_used += 1
            break

        if faces_used >= MAX_FRAMES:
            break

    cap.release()

# ================= SCAN DATASET =================
print("\n🔍 Scanning dataset...")
video_files = []

for root, _, files in os.walk(DATASET_PATH):
    for file in files:
        if file.endswith(".mp4"):
            video_files.append(os.path.join(root, file))

print(f"✅ Total videos found: {len(video_files)}")

video_files = video_files[:MAX_VIDEOS]
print(f"⚠️ Using only first {len(video_files)} videos\n")

# ================= FACE EXTRACTION =================
print("🚀 Starting face extraction...\n")
processed = 0

for video_path in tqdm(video_files, desc="Processing videos"):
    file = os.path.basename(video_path)
    emotion = file.split("-")[2]

    before = len(X)
    extract_faces(video_path, emotion)
    after = len(X)

    processed += 1
    print(f"✔ [{processed}/{len(video_files)}] {file} | Faces added: {after - before}")

# ================= SUMMARY =================
print("\n📊 EXTRACTION SUMMARY")
print("-" * 40)
print(f"Total videos processed : {processed}")
print(f"Total face frames      : {len(X)}")
print("✅ Face extraction completed successfully\n")

if len(X) == 0:
    raise RuntimeError("❌ No faces extracted.")

# ================= PREPARE DATA =================
print("🧮 Preparing data for training...")

X = np.asarray(X, dtype=np.float32) / 255.0
y = to_categorical(labels, num_classes=8)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=np.argmax(y, axis=1),
    random_state=42
)

# 🔥 IMPORTANT: SAVE TEST DATA FOR EVALUATION
os.makedirs("../data", exist_ok=True)
np.save("../data/X_test.npy", X_test)
np.save("../data/y_test.npy", y_test)

print("✅ Test data saved in /data folder")

# ================= MODEL =================
base = MobileNetV2(
    weights="imagenet",
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)
base.trainable = False

x = GlobalAveragePooling2D()(base.output)
x = Dense(128, activation="relu")(x)
x = Dropout(0.4)(x)
output = Dense(8, activation="softmax")(x)

model = Model(base.input, output)
model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# ================= TRAIN =================
print("\n🧠 Model training started...\n")

model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE
)

# ================= FINAL EVALUATION =================
test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)

print("\n📈 MODEL EVALUATION")
print("-" * 30)
print(f"Test Accuracy : {test_acc * 100:.2f}%")
print(f"Test Loss     : {test_loss:.4f}")

# ================= SAVE MODEL =================
os.makedirs("../models", exist_ok=True)
model.save("../models/video_emotion_model.h5")

print("\n💾 Model saved at: ../models/video_emotion_model.h5")
print("✅ PROJECT PIPELINE COMPLETED SUCCESSFULLY 😊")
