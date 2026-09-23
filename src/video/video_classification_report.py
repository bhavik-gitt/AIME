from sklearn.metrics import classification_report
from video_confusion_matrix import y, y_pred, emotion_map

report = classification_report(
    y, y_pred,
    target_names=list(emotion_map.keys())
)

print(report)

with open("../../assets/video_report.txt", "w") as f:
    f.write(report)

print("✅ Saved report")