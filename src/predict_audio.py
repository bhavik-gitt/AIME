# ================================
# AUDIO EMOTION PREDICTION (FIXED)
# ================================
import os
import librosa
import numpy as np
import tensorflow as tf

# ---------------- CONFIG ----------------
MODEL_PATH   = r"../models/audio_emotion_model.h5"
AUDIO_FILE   = r"C:\Btech It Sem 6\PROJECT\dataset\CREMA-D\AudioWAV\1001_DFA_ANG_XX.wav"
SAMPLE_RATE  = 16000   # ✅ match training
DURATION     = 3       # ✅ match training
N_MELS       = 64      # ✅ match training
MAX_LEN      = 128     # ✅ match training
# ----------------------------------------

emotion_labels = ["angry", "disgust", "fear", "happy", "neutral", "sad"]

# ================= LOAD MODEL =================
print("\n🔄 Loading audio emotion model...")
model = tf.keras.models.load_model(MODEL_PATH)
print("✅ Model loaded successfully")

# ================= FEATURE EXTRACTION (same as training) =================
def extract_logmel(file_path):
    audio, sr = librosa.load(file_path, sr=SAMPLE_RATE, duration=DURATION)
    
    mel = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=N_MELS)
    logmel = librosa.power_to_db(mel)

    # Fix time dimension — same as training
    if logmel.shape[1] < MAX_LEN:
        pad_width = MAX_LEN - logmel.shape[1]
        logmel = np.pad(logmel, ((0, 0), (0, pad_width)))
    else:
        logmel = logmel[:, :MAX_LEN]

    return logmel  # shape: (64, 128)

# ================= PREDICT =================
if not os.path.exists(AUDIO_FILE):
    raise FileNotFoundError(f"❌ Audio file not found: {AUDIO_FILE}")

print(f"\n🎧 Testing audio: {os.path.basename(AUDIO_FILE)}")

features = extract_logmel(AUDIO_FILE)
features = features[..., np.newaxis]        # (64, 128, 1)
features = np.expand_dims(features, axis=0) # (1, 64, 128, 1) ✅

prediction = model.predict(features, verbose=0)[0]
emotion_index = np.argmax(prediction)
emotion = emotion_labels[emotion_index]
confidence = prediction[emotion_index]

# ================= OUTPUT =================
print("\n🎯 Prediction Result")
print("-" * 30)
print(f"Emotion    : {emotion}")
print(f"Confidence : {confidence * 100:.2f}%\n")

for i, emo in enumerate(emotion_labels):
    bar = "█" * int(prediction[i] * 30)
    print(f"{emo:<8}: {prediction[i]:.4f}  {bar}")