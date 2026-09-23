import os
import librosa
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import to_categorical

# ================= CONFIG =================
DATASET_PATH = r"C:\Btech It Sem 6\PROJECT\dataset\CREMA-D\AudioWAV"
MODEL_PATH = r"..\models\audio_emotion_model.h5"
SAMPLE_RATE = 16000
DURATION = 3
N_MELS = 64
MAX_LEN = 128
# =========================================

emotion_map = {
    "ANG": "angry",
    "DIS": "disgust",
    "FEA": "fear",
    "HAP": "happy",
    "NEU": "neutral",
    "SAD": "sad"
}

def extract_logmel(file_path):
    audio, sr = librosa.load(
        file_path, sr=SAMPLE_RATE, duration=DURATION
    )
    mel = librosa.feature.melspectrogram(
        y=audio, sr=sr, n_mels=N_MELS
    )
    logmel = librosa.power_to_db(mel)

    if logmel.shape[1] < MAX_LEN:
        pad = MAX_LEN - logmel.shape[1]
        logmel = np.pad(logmel, ((0, 0), (0, pad)))
    else:
        logmel = logmel[:, :MAX_LEN]

    return logmel

print("\n📥 Loading dataset for evaluation...")

X, y = [], []

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
    X.append(extract_logmel(file_path))
    y.append(emotion_map[emo_code])

X = np.array(X)[..., np.newaxis]

le = LabelEncoder()
y = le.fit_transform(y)
y_cat = to_categorical(y)

# SAME split as training
_, X_test, _, y_test = train_test_split(
    X, y_cat,
    test_size=0.2,
    stratify=y,
    random_state=42
)

print("\n🔄 Loading trained model...")
model = load_model(MODEL_PATH)

print("🧠 Predicting emotions...")
y_pred = model.predict(X_test)
y_pred_labels = np.argmax(y_pred, axis=1)
y_true = np.argmax(y_test, axis=1)

# ================= REPORT =================
print("\n📊 CLASSIFICATION REPORT\n")
print(classification_report(
    y_true, y_pred_labels,
    target_names=le.classes_
))

# ================= CONFUSION MATRIX =================
cm = confusion_matrix(y_true, y_pred_labels)

plt.figure(figsize=(8, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=le.classes_,
    yticklabels=le.classes_
)

plt.title("Audio Emotion Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.show()
