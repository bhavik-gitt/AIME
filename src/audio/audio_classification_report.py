from sklearn.metrics import classification_report
import numpy as np

# Reuse from confusion matrix file
from audio_confusion_matrix import y, y_pred, emotion_map

report = classification_report(
    y, y_pred,
    target_names=list(emotion_map.keys())
)

print(report)

with open("../../assets/audio_report.txt", "w") as f:
    f.write(report)

print("✅ Saved report")