import cv2
import numpy as np
import tensorflow as tf

# ================= CONFIG =================
MODEL_PATH = r"..\models\video_emotion_model.h5"
IMG_SIZE = 160
# =========================================

emotion_labels = [
    "neutral", "calm", "happy", "sad",
    "angry", "fear", "disgust", "surprise"
]

print("🔄 Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)
print("✅ Model loaded")

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

cap = cv2.VideoCapture(0)

cv2.namedWindow("Emotion Recognition (Press Q or ESC to Exit)", cv2.WINDOW_NORMAL)

print("🎥 Webcam started (Press Q or ESC to quit)")

predictions = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=3,
        minSize=(80, 80)
    )

    for (x, y, w, h) in faces:
        face = frame[y:y+h, x:x+w]
        if face.size == 0:
            continue

        face = cv2.resize(face, (IMG_SIZE, IMG_SIZE))
        face = face.astype("float32") / 255.0
        face_input = np.expand_dims(face, axis=0)

        pred = model.predict(face_input, verbose=0)[0]
        predictions.append(pred)

        emotion = emotion_labels[np.argmax(pred)]
        confidence = np.max(pred) * 100

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
        cv2.putText(
            frame,
            f"{emotion} ({confidence:.1f}%)",
            (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,255,0),
            2
        )

    cv2.imshow("Emotion Recognition (Press Q or ESC to Exit)", frame)

    key = cv2.waitKey(10)
    if key == ord('q') or key == 27:  # q or ESC
        break

cap.release()
cv2.destroyAllWindows()

# ===== FINAL SUMMARY (IMPROVED) =====
if len(predictions) > 10:
    preds = np.array(predictions)

    # Ignore low-confidence frames
    confident_preds = preds[np.max(preds, axis=1) > 0.5]

    if len(confident_preds) == 0:
        confident_preds = preds

    avg_pred = np.mean(confident_preds, axis=0)
    final_emotion = emotion_labels[np.argmax(avg_pred)]
    final_conf = np.max(avg_pred) * 100

    print("\n🎯 FINAL SESSION RESULT (SMOOTHED)")
    print("-" * 35)
    print(f"Emotion    : {final_emotion}")
    print(f"Confidence : {final_conf:.2f}%")
else:
    print("\n❌ Not enough frames for reliable prediction.")
