import os
import pandas as pd
import matplotlib.pyplot as plt

DATASET = "../../dataset/CREMA-D/AudioWAV"
SAVE = "../../assets/audio_class_distribution.png"

if not os.path.exists(DATASET):
    print("❌ Dataset path not found:", DATASET)
    exit()

emotion_map = {
    "ANG": "angry",
    "DIS": "disgust",
    "FEA": "fear",
    "HAP": "happy",
    "NEU": "neutral",
    "SAD": "sad"
}

emotions = []

for file in os.listdir(DATASET):
    if file.endswith(".wav"):
        parts = file.split("_")
        if len(parts) > 2 and parts[2] in emotion_map:
            emotions.append(emotion_map[parts[2]])

df = pd.DataFrame({"Emotion": emotions})

plt.figure()
df["Emotion"].value_counts().plot(kind='bar')
plt.title("Audio Emotion Distribution")
plt.xlabel("Emotion")
plt.ylabel("Count")
plt.savefig(SAVE)
plt.close()

print("✅ Saved:", SAVE)