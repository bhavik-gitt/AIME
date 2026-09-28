from flask import Flask, render_template, request, jsonify, Response
import os, uuid
from utils.audio_utils import predict_audio_emotion
from utils.video_utils  import generate_video_frames, analyze_video_file, get_live_emotion, stop_stream
from utils.recommendations import get_recommendation, get_all_recommendations

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── DASHBOARD ────────────
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# ── AUDIO ─────────────
@app.route("/audio")
def audio():
    return render_template("audio.html")

@app.route("/audio/predict", methods=["POST"])
def audio_predict():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f    = request.files["file"]
    name = f.filename if f.filename else f"rec_{uuid.uuid4().hex[:8]}.wav"
    path = os.path.join(UPLOAD_FOLDER, name)
    f.save(path)
    try:
        emotion, confidence = predict_audio_emotion(path)
        return jsonify({
            "emotion":     emotion,
            "confidence":  round(confidence, 1),
            "suggestions": get_all_recommendations(emotion),
            "emoji":       _emoji(emotion, "audio")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── VIDEO ───────────
@app.route("/video")
def video():
    return render_template("video.html")

@app.route("/video_feed")
def video_feed():
    """MJPEG stream — must be wrapped in Response with correct mimetype."""
    return Response(
        generate_video_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/video/stop", methods=["POST"])
def video_stop():
    stop_stream()
    return jsonify({"ok": True})

@app.route("/video/live_emotion")
def video_live_emotion():
    emotion, confidence = get_live_emotion()
    return jsonify({
        "emotion":     emotion,
        "confidence":  round(confidence, 1),
        "suggestions": get_all_recommendations(emotion),
        "emoji":       _emoji(emotion, "video")
    })

@app.route("/video/predict", methods=["POST"])
def video_predict():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f    = request.files["file"]
    path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex[:8]}_{f.filename}")
    f.save(path)
    try:
        emotion, confidence = analyze_video_file(path)
        return jsonify({
            "emotion":     emotion,
            "confidence":  round(confidence, 1),
            "suggestions": get_all_recommendations(emotion),
            "emoji":       _emoji(emotion, "video")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── ANALYTICS / ABOUT ──────────
@app.route("/analytics")
def analytics():
    return render_template("analytics.html")

@app.route("/about")
def about():
    return render_template("about.html")

# ── HELPER ────────
def _emoji(emotion, mode="audio"):
    m = {
        "audio": {"angry":"😠","disgust":"🤢","fear":"😨","happy":"😊","neutral":"😐","sad":"😢"},
        "video": {"neutral":"😐","calm":"😌","happy":"😊","sad":"😢",
                  "angry":"😠","fear":"😨","disgust":"🤢","surprise":"😲"}
    }
    return m.get(mode, m["audio"]).get(emotion, "🤔")

if __name__ == "__main__":
    app.run(debug=True)
