import cv2
import numpy as np
from tensorflow.keras.models import load_model

MODEL_PATH = "../models/video_emotion_model.h5"
IMG_SIZE   = 160

model    = load_model(MODEL_PATH)
emotions = ["neutral", "calm", "happy", "sad", "angry", "fear", "disgust", "surprise"]

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ── Shared live state ──────────────────────────────────────
_live_emotion    = "neutral"
_live_confidence = 0.0
_streaming       = False


def get_live_emotion():
    return _live_emotion, _live_confidence


def _predict_face(face_bgr):
    """
    Predict emotion from a face crop (BGR image).
    Resize to 160×160, normalise, predict.
    CRITICAL FIX: we predict on the face crop ONLY, not the full frame.
    """
    face = cv2.resize(face_bgr, (IMG_SIZE, IMG_SIZE)).astype("float32") / 255.0
    face = np.expand_dims(face, axis=0)   # (1, 160, 160, 3)
    pred = model.predict(face, verbose=0)[0]
    idx  = int(np.argmax(pred))
    return emotions[idx], float(pred[idx]) * 100


def generate_video_frames():
    """
    MJPEG stream — detect face bounding box, predict ONLY on face crop,
    draw coloured box + label, update shared live state.
    """
    global _live_emotion, _live_confidence, _streaming
    _streaming = True
    cap = cv2.VideoCapture(0)
    frame_n = 0

    while _streaming:
        ok, frame = cap.read()
        if not ok:
            break

        frame_n += 1
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60)
        )

        # Predict every 3rd frame to keep stream smooth
        if frame_n % 3 == 0 and len(faces) > 0:
            x, y, w, h = faces[0]
            crop = frame[y:y+h, x:x+w]
            if crop.size > 0:
                # ✅ predict on FACE CROP not full frame
                _live_emotion, _live_confidence = _predict_face(crop)

        # Draw box + label for every detected face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (96, 165, 250), 2)
            label = f"{_live_emotion}  {_live_confidence:.0f}%"
            # Background for text readability
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
            cv2.rectangle(frame, (x, y-th-12), (x+tw+8, y), (96, 165, 250), -1)
            cv2.putText(frame, label, (x+4, y-6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (5, 9, 15), 2)

        ret, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
               + buf.tobytes() + b"\r\n")

    cap.release()
    _streaming = False


def stop_stream():
    global _streaming
    _streaming = False


def analyze_video_file(path):
    """
    Analyze uploaded video file — sample a frame every 0.5 s,
    detect face, predict on face crop only, average predictions.
    Returns (dominant_emotion, avg_confidence).
    """
    cap   = cv2.VideoCapture(path)
    fps   = cap.get(cv2.CAP_PROP_FPS) or 25.0
    step  = max(1, int(fps * 0.5))   # one sample per 0.5 s

    all_preds = []
    frame_n   = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if frame_n % step == 0:
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=4, minSize=(50, 50)
            )
            if len(faces) > 0:
                x, y, w, h = faces[0]
                crop = frame[y:y+h, x:x+w]
                if crop.size > 0:
                    face = cv2.resize(crop, (IMG_SIZE, IMG_SIZE)).astype("float32") / 255.0
                    face = np.expand_dims(face, axis=0)
                    pred = model.predict(face, verbose=0)[0]
                    all_preds.append(pred)
        frame_n += 1

    cap.release()

    if not all_preds:
        # No face found — return neutral with 0 confidence
        return "neutral", 0.0

    avg = np.mean(all_preds, axis=0)
    idx = int(np.argmax(avg))
    return emotions[idx], float(avg[idx]) * 100
