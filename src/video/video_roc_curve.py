from sklearn.preprocessing import label_binarize
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
from video_confusion_matrix import y, pred, emotion_map

y_bin = label_binarize(y, classes=list(range(len(emotion_map))))

plt.figure()

for i in range(len(emotion_map)):
    fpr, tpr, _ = roc_curve(y_bin[:, i], pred[:, i])
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, label=f"{list(emotion_map.keys())[i]} ({roc_auc:.2f})")

plt.plot([0,1],[0,1],'--')
plt.legend()
plt.title("Video ROC Curve")
plt.savefig("../../assets/video_roc_curve.png")
plt.close()

print("✅ Saved ROC")