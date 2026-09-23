import numpy as np
import tensorflow as tf
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt

# Load data saved during training
X_test = np.load("../data/X_test.npy")
y_test = np.load("../data/y_test.npy")

model = tf.keras.models.load_model("../models/video_emotion_model.h5")

y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)
y_true = np.argmax(y_test, axis=1)

emotion_labels = [
    "neutral","calm","happy","sad",
    "angry","fear","disgust","surprise"
]

cm = confusion_matrix(y_true, y_pred_classes)

plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt="d",
            xticklabels=emotion_labels,
            yticklabels=emotion_labels)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix - Video Emotion Recognition")
plt.show()

print("\nClassification Report:\n")
print(classification_report(y_true, y_pred_classes, target_names=emotion_labels))

# for video