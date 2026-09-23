import os
import librosa
import numpy as np
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D, MaxPooling2D, BatchNormalization,
    Reshape, Bidirectional, LSTM,
    Dense, Dropout
)
from tensorflow.keras.callbacks import EarlyStopping

# ================= CONFIG =================
DATASET_PATH = r"C:\Btech It Sem 6\PROJECT\dataset\CREMA-D\AudioWAV"
SAMPLE_RATE = 16000
DURATION = 3
N_MELS = 64
MAX_LEN = 128
EPOCHS = 30
BATCH_SIZE = 32
# =========================================

emotion_map = {
    "ANG": "angry",
    "DIS": "disgust",
    "FEA": "fear",
    "HAP": "happy",
    "NEU": "neutral",
    "SAD": "sad"
}

X, y = [], []

print("\n🎧 Loading CREMA-D audio files...\n")

def extract_logmel(file_path):
    audio, sr = librosa.load(
        file_path, sr=SAMPLE_RATE, duration=DURATION
    )
    mel = librosa.feature.melspectrogram(
        y=audio, sr=sr, n_mels=N_MELS
    )
    logmel = librosa.power_to_db(mel)

    # Fix time dimension
    if logmel.shape[1] < MAX_LEN:
        pad_width = MAX_LEN - logmel.shape[1]
        logmel = np.pad(logmel, ((0, 0), (0, pad_width)))
    else:
        logmel = logmel[:, :MAX_LEN]

    return logmel

for file in tqdm(os.listdir(DATASET_PATH)):
    if not file.endswith(".wav"):
        continue

    parts = file.split("_")
    if len(parts) < 3:
        continue

    emo_code = parts[2]
    if emo_code not in emotion_map:
        continue

    file_path = os.path.join(DATASET_PATH, file)
    features = extract_logmel(file_path)

    X.append(features)
    y.append(emotion_map[emo_code])

X = np.array(X)
X = X[..., np.newaxis]  # (samples, mel, time, 1)

le = LabelEncoder()
y = le.fit_transform(y)
y = to_categorical(y)

print("\n📊 DATA SUMMARY")
print("Samples:", X.shape[0])
print("Input shape:", X.shape[1:])
print("Classes:", le.classes_)

# ================= SPLIT =================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2,
    stratify=y.argmax(axis=1),
    random_state=42
)

# ================= MODEL =================
model = Sequential([
    Conv2D(32, (3, 3), activation="relu", padding="same",
           input_shape=X.shape[1:]),
    BatchNormalization(),
    MaxPooling2D((2, 2)),

    Conv2D(64, (3, 3), activation="relu", padding="same"),
    BatchNormalization(),
    MaxPooling2D((2, 2)),

    Reshape((-1, 64)),
    Bidirectional(LSTM(64, return_sequences=False)),

    Dense(128, activation="relu"),
    Dropout(0.4),
    Dense(y.shape[1], activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# ================= TRAIN =================
print("\n🧠 Training audio emotion model...\n")

history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=[
        EarlyStopping(
            monitor="val_loss",
            patience=6,
            restore_best_weights=True
        )
    ]
)

# ================= EVALUATE =================
loss, acc = model.evaluate(X_test, y_test, verbose=0)

print("\n📈 AUDIO MODEL PERFORMANCE")
print("--------------------------------")
print(f"Test Accuracy : {acc*100:.2f}%")
print(f"Test Loss     : {loss:.4f}")

# ================= SAVE =================
os.makedirs("../models", exist_ok=True)
model.save("../models/audio_emotion_model.h5")

np.save("../models/audio_classes.npy", le.classes_)

print("\n💾 Model saved at: ../models/audio_emotion_model.h5")
print("✅ AUDIO TRAINING COMPLETED SUCCESSFULLY 🎉")
