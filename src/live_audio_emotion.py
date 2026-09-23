import sounddevice as sd
import numpy as np
import librosa
import queue
import threading
import tkinter as tk
from tkinter import ttk
from tensorflow.keras.models import load_model

# ================= CONFIG =================
MODEL_PATH = r"..\models\audio_emotion_model.h5"
CLASSES_PATH = r"..\models\audio_classes.npy"

SAMPLE_RATE = 16000
DURATION = 3
N_MELS = 64
MAX_LEN = 128
# =========================================

emotion_labels = np.load(CLASSES_PATH)
model = load_model(MODEL_PATH)

audio_queue = queue.Queue()
running = False
emotion_history = []

# Emotion → Color mapping
EMOTION_COLORS = {
    "angry": "#e74c3c",
    "disgust": "#8e44ad",
    "fear": "#2c3e50",
    "happy": "#f1c40f",
    "neutral": "#3498db",
    "sad": "#34495e"
}

# ---------------- AUDIO ----------------
def extract_logmel(audio):
    mel = librosa.feature.melspectrogram(
        y=audio, sr=SAMPLE_RATE, n_mels=N_MELS
    )
    logmel = librosa.power_to_db(mel)

    if logmel.shape[1] < MAX_LEN:
        pad = MAX_LEN - logmel.shape[1]
        logmel = np.pad(logmel, ((0, 0), (0, pad)))
    else:
        logmel = logmel[:, :MAX_LEN]

    return logmel[..., np.newaxis]

def audio_callback(indata, frames, time, status):
    if running:
        audio_queue.put(indata[:, 0].copy())

def listen_audio():
    buffer = np.zeros(0)

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=audio_callback
    ):
        while running:
            data = audio_queue.get()
            buffer = np.concatenate((buffer, data))

            if len(buffer) >= SAMPLE_RATE * DURATION:
                chunk = buffer[:SAMPLE_RATE * DURATION]
                buffer = buffer[SAMPLE_RATE * DURATION:]

                features = extract_logmel(chunk)
                features = np.expand_dims(features, axis=0)

                preds = model.predict(features, verbose=0)[0]
                idx = np.argmax(preds)

                emotion = emotion_labels[idx]
                confidence = preds[idx] * 100

                update_ui(emotion, confidence)

# ---------------- UI UPDATE ----------------
def update_ui(emotion, confidence):
    color = EMOTION_COLORS.get(emotion, "#2c3e50")

    emotion_label.config(
        text=emotion.upper(),
        foreground=color
    )

    confidence_label.config(
        text=f"Confidence: {confidence:.2f}%"
    )

    confidence_bar["value"] = confidence

    # Emotion history
    emotion_history.insert(0, emotion.capitalize())
    del emotion_history[5:]

    history_text.set("\n".join(emotion_history))

# ---------------- CONTROLS ----------------
def start_listening():
    global running
    if not running:
        running = True
        mic_status.config(text="● Mic: Listening", foreground="green")
        threading.Thread(target=listen_audio, daemon=True).start()

def stop_listening():
    global running
    running = False
    mic_status.config(text="● Mic: Stopped", foreground="red")

# ---------------- WINDOW ----------------
root = tk.Tk()
root.title("AIME : AI that understands the real you")
root.geometry("520x420")
root.configure(bg="#f4f6f7")
root.resizable(False, False)

# Title
title = tk.Label(
    root,
    text="🎧 MindWealth – Audio Emotion AI ",
    font=("Segoe UI", 18, "bold"),
    bg="#f4f6f7"
)
title.pack(pady=15)

# Emotion Card
card = tk.Frame(
    root,
    bg="white",
    bd=2,
    relief="ridge"
)
card.pack(pady=10, padx=20, fill="x")

emotion_label = tk.Label(
    card,
    text="---",
    font=("Segoe UI", 28, "bold"),
    bg="white"
)
emotion_label.pack(pady=15)

confidence_label = tk.Label(
    card,
    text="Confidence: 0.00%",
    font=("Segoe UI", 12),
    bg="white"
)
confidence_label.pack()

confidence_bar = ttk.Progressbar(
    card,
    length=350,
    maximum=100
)
confidence_bar.pack(pady=15)

# History
history_frame = tk.Frame(root, bg="#f4f6f7")
history_frame.pack(pady=10)

tk.Label(
    history_frame,
    text="Recent Emotions",
    font=("Segoe UI", 12, "bold"),
    bg="#f4f6f7"
).pack()

history_text = tk.StringVar(value="")
tk.Label(
    history_frame,
    textvariable=history_text,
    font=("Segoe UI", 11),
    bg="#f4f6f7",
    justify="left"
).pack()

# Mic Status
mic_status = tk.Label(
    root,
    text="● Mic: Idle",
    font=("Segoe UI", 11),
    fg="red",
    bg="#f4f6f7"
)
mic_status.pack(pady=10)

# Buttons
btn_frame = tk.Frame(root, bg="#f4f6f7")
btn_frame.pack(pady=10)

tk.Button(
    btn_frame,
    text="▶ Start Mic",
    font=("Segoe UI", 11),
    width=12,
    command=start_listening
).grid(row=0, column=0, padx=10)

tk.Button(
    btn_frame,
    text="⏹ Stop",
    font=("Segoe UI", 11),
    width=12,
    command=stop_listening
).grid(row=0, column=1, padx=10)

root.mainloop()
