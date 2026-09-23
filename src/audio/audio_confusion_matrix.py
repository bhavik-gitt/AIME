import os
import numpy as np
import librosa
import seaborn as sns
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix

DATASET = "../../dataset/CREMA-D/AudioWAV"
MODEL = "../../models/audio_emotion_model.h5"
SAVE = "../../assets/audio_confusion_matrix.png"

emotion_map = {"ANG":0,"DIS":1,"FEA":2,"HAP":3,"NEU":4,"SAD":5}
labels = list(emotion_map.keys())

def extract(file):
    y, sr = librosa.load(file, duration=3, offset=0.5)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=64)
    mel = librosa.power_to_db(mel)

    if mel.shape[1] < 128:
        mel = np.pad(mel, ((0,0),(0,128-mel.shape[1])))
    else:
        mel = mel[:, :128]

    return mel

X, y = [], []

for file in os.listdir(DATASET):
    if file.endswith(".wav"):
        emo = file.split("_")[2]
        if emo in emotion_map:
            X.append(extract(os.path.join(DATASET, file)))
            y.append(emotion_map[emo])

X = np.array(X).reshape(-1,64,128,1)
y = np.array(y)

model = load_model(MODEL)

pred = model.predict(X, verbose=0)
y_pred = np.argmax(pred, axis=1)

cm = confusion_matrix(y, y_pred)

plt.figure()
sns.heatmap(cm, annot=True, fmt='d',
            xticklabels=emotion_map.keys(),
            yticklabels=emotion_map.keys())

plt.title("Audio Confusion Matrix")
plt.savefig(SAVE)
plt.close()

print("✅ Saved:", SAVE)