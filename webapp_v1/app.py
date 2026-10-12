from flask import Response, jsonify

from webapp_v1.aime import create_app
from webapp_v1.utils.recommendations import get_all_recommendations


app = create_app()


@app.route("/video_feed")
def video_feed():
    from webapp_v1.utils.video_utils import generate_video_frames

    return Response(generate_video_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/video/stop", methods=["POST"])
def video_stop():
    from webapp_v1.utils.video_utils import stop_stream

    stop_stream()
    return jsonify({"ok": True})


@app.route("/video/live_emotion")
def video_live_emotion():
    from webapp_v1.utils.video_utils import get_live_emotion

    emotion, confidence = get_live_emotion()
    return jsonify(
        {
            "emotion": emotion,
            "confidence": round(confidence, 1),
            "suggestions": get_all_recommendations(emotion),
            "emoji": _emoji(emotion, "video"),
        }
    )


def _emoji(emotion, mode="audio"):
    m = {
        "audio": {"angry": "😠", "disgust": "🤢", "fear": "😨", "happy": "😊", "neutral": "😐", "sad": "😢"},
        "video": {"neutral": "😐", "calm": "😌", "happy": "😊", "sad": "😢", "angry": "😠", "fear": "😨", "disgust": "🤢", "surprise": "😲"},
    }
    return m.get(mode, m["audio"]).get(emotion, "🤔")


if __name__ == "__main__":
    app.run(debug=True)
