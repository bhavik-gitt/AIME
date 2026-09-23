import os
import cv2
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix

DATASET = "../../dataset/RAVDESS dataset"
MODEL = "../../models/video_emotion_model.h5"
SAVE = "../../assets/video_confusion_matrix.png"

emotion_map = {
    "01":0,"02":1,"03":2,"04":3,
    "05":4,"06":5,"07":6,"08":7
}

X, y = [], []

for root, _, files in os.walk(DATASET):
    for file in files:
        if file.endswith(".mp4"):
            emo = file.split("-")[2]
            if emo in emotion_map:
                path = os.path.join(root, file)

                cap = cv2.VideoCapture(path)
                ret, frame = cap.read()
                cap.release()

                if ret:
                    frame = cv2.resize(frame, (160,160))
                    X.append(frame)
                    y.append(emotion_map[emo])

X = np.array(X)/255.0
y = np.array(y)

model = load_model(MODEL)

pred = model.predict(X, verbose=0)
y_pred = np.argmax(pred, axis=1)

cm = confusion_matrix(y, y_pred)

plt.figure()
sns.heatmap(cm, annot=True, fmt='d',
            xticklabels=emotion_map.keys(),
            yticklabels=emotion_map.keys())

plt.title("Video Confusion Matrix")
plt.savefig(SAVE)
plt.close()

print("✅ Saved:", SAVE)