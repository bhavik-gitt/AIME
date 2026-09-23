import numpy as np
import librosa
from tensorflow.keras.models import load_model

# ── CONFIG — matches your actual training script exactly ──
MODEL_PATH  = "../models/audio_emotion_model.h5"
SAMPLE_RATE = 16000
DURATION    = 3
N_MELS      = 64
MAX_LEN     = 128

model = load_model(MODEL_PATH)

# Load classes from saved npy if available, else use default order
try:
    _classes = np.load("../models/audio_classes.npy", allow_pickle=True)
    emotions = list(_classes)
except Exception:
    emotions = ["angry", "disgust", "fear", "happy", "neutral", "sad"]


def extract_features(file_path):
    """
    Log-Mel Spectrogram extraction — matches your training script exactly.
    Training used: melspectrogram → power_to_db → pad/crop to (64, 128) → add channel.
    """
    audio, sr = librosa.load(file_path, sr=SAMPLE_RATE, duration=DURATION)

    # Ensure fixed length
    target_len = int(SAMPLE_RATE * DURATION)
    if len(audio) < target_len:
        audio = np.pad(audio, (0, target_len - len(audio)))
    else:
        audio = audio[:target_len]

    mel    = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=N_MELS)
    logmel = librosa.power_to_db(mel)

    # Fix time dimension — same as training
    if logmel.shape[1] < MAX_LEN:
        logmel = np.pad(logmel, ((0, 0), (0, MAX_LEN - logmel.shape[1])))
    else:
        logmel = logmel[:, :MAX_LEN]

    return logmel  # shape: (64, 128)


def predict_audio_emotion(file_path):
    """
    Predict emotion from audio file.
    Returns (emotion_string, confidence_float_0_to_100).
    """
    features = extract_features(file_path)
    features = features[..., np.newaxis]          # (64, 128, 1)
    features = np.expand_dims(features, axis=0)   # (1, 64, 128, 1)

    pred = model.predict(features, verbose=0)[0]
    idx  = int(np.argmax(pred))
    return emotions[idx], float(pred[idx]) * 100
