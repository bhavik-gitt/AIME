import os
import pandas as pd
import matplotlib.pyplot as plt

DATASET = "../../dataset/RAVDESS dataset"
SAVE = "../../assets/video_class_distribution.png"

emotion_map = {
    "01":"neutral","02":"calm","03":"happy","04":"sad",
    "05":"angry","06":"fear","07":"disgust","08":"surprise"
}

emotions = []

for root, _, files in os.walk(DATASET):
    for file in files:
        if file.endswith(".mp4"):
            parts = file.split("-")
            if len(parts) > 2 and parts[2] in emotion_map:
                emotions.append(emotion_map[parts[2]])

df = pd.DataFrame({"Emotion": emotions})

plt.figure()
df["Emotion"].value_counts().plot(kind='bar')
plt.title("Video Emotion Distribution")
plt.xlabel("Emotion")
plt.ylabel("Count")
plt.savefig(SAVE)
plt.close()

print("✅ Saved:", SAVE)