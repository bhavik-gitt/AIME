from __future__ import annotations

import csv
import io
from datetime import datetime, UTC
from pathlib import Path
import uuid

from flask import Blueprint, Response, current_app, g, jsonify, request
from sqlalchemy import func

from ..extensions import db
from ..models import AnalysisNote, EmotionAnalysis, UserPreference
from ..security import auth_required
bp = Blueprint("analysis_api", __name__)


def _upload_dir() -> Path:
    root = Path(__file__).resolve().parents[2]
    out = root / "uploads"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _analysis_payload(row: EmotionAnalysis):
    note = row.notes[0] if row.notes else None
    return {
        "id": row.id,
        "modality": row.modality,
        "predictedEmotion": row.predicted_emotion,
        "confidenceScore": row.confidence_score,
        "classProbabilities": row.class_probabilities or {},
        "modelVersion": row.model_version,
        "processingStatus": row.processing_status,
        "durationSeconds": row.duration_seconds,
        "createdAt": row.created_at.isoformat(),
        "updatedAt": row.updated_at.isoformat(),
        "note": {
            "id": note.id,
            "userReportedMood": note.user_reported_mood,
            "personalReflection": note.personal_reflection,
            "updatedAt": note.updated_at.isoformat(),
        } if note else None,
    }


def _store_analysis(user_id: int, modality: str, emotion: str, confidence: float, probabilities: dict, duration: float | None = None):
    row = EmotionAnalysis(
        user_id=user_id,
        modality=modality,
        predicted_emotion=emotion,
        confidence_score=round(confidence, 4),
        class_probabilities=probabilities,
        model_version="aime-v1",
        processing_status="completed",
        duration_seconds=duration,
    )
    db.session.add(row)
    db.session.commit()
    return row


@bp.post("/analysis/audio/predict")
@auth_required
def predict_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    uploaded = request.files["file"]
    if not uploaded.filename:
        return jsonify({"error": "Missing filename"}), 400

    ext = Path(uploaded.filename).suffix.lower()
    if ext not in {".wav", ".mp3", ".m4a", ".ogg"}:
        return jsonify({"error": "Unsupported audio format"}), 400

    path = _upload_dir() / f"{uuid.uuid4().hex}{ext}"
    uploaded.save(path)

    from webapp_v1.utils.audio_utils import predict_audio_with_probs

    emotion, confidence, probs = predict_audio_with_probs(str(path))
    saved = None
    pref = UserPreference.query.filter_by(user_id=g.current_user.id).first()
    should_save = request.args.get("save") == "true" or (pref.auto_save_analysis if pref else False)
    if should_save:
        saved = _store_analysis(g.current_user.id, "audio", emotion, confidence, probs)

    return jsonify({
        "success": True,
        "result": {
            "modality": "audio",
            "emotion": emotion,
            "confidence": round(confidence, 2),
            "classProbabilities": probs,
            "savedAnalysisId": saved.id if saved else None,
            "disclaimer": "Predictions are probabilistic estimates and are not a diagnosis.",
        },
    })


@bp.post("/analysis/video/predict")
@auth_required
def predict_video():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    uploaded = request.files["file"]
    if not uploaded.filename:
        return jsonify({"error": "Missing filename"}), 400

    ext = Path(uploaded.filename).suffix.lower()
    if ext not in {".mp4", ".mov", ".avi", ".mkv"}:
        return jsonify({"error": "Unsupported video format"}), 400

    path = _upload_dir() / f"{uuid.uuid4().hex}{ext}"
    uploaded.save(path)

    from webapp_v1.utils.video_utils import analyze_video_file_with_probs

    emotion, confidence, probs = analyze_video_file_with_probs(str(path))
    saved = None
    pref = UserPreference.query.filter_by(user_id=g.current_user.id).first()
    should_save = request.args.get("save") == "true" or (pref.auto_save_analysis if pref else False)
    if should_save:
        saved = _store_analysis(g.current_user.id, "video", emotion, confidence, probs)

    return jsonify({
        "success": True,
        "result": {
            "modality": "video",
            "emotion": emotion,
            "confidence": round(confidence, 2),
            "classProbabilities": probs,
            "savedAnalysisId": saved.id if saved else None,
            "disclaimer": "Predictions are probabilistic estimates and are not a diagnosis.",
        },
    })


@bp.post("/analysis/save")
@auth_required
def save_analysis():
    data = request.get_json(silent=True) or {}
    modality = data.get("modality")
    emotion = data.get("predictedEmotion")
    confidence = data.get("confidenceScore")
    probs = data.get("classProbabilities") or {}
    duration = data.get("durationSeconds")

    if modality not in {"audio", "video"}:
        return jsonify({"error": "Invalid modality"}), 400
    if not emotion:
        return jsonify({"error": "predictedEmotion is required"}), 400
    try:
        confidence = float(confidence)
    except Exception:
        return jsonify({"error": "confidenceScore must be numeric"}), 400

    row = _store_analysis(g.current_user.id, modality, emotion, confidence, probs, duration)
    return jsonify({"success": True, "analysis": _analysis_payload(row)}), 201


@bp.get("/analysis/<int:analysis_id>")
@auth_required
def get_analysis(analysis_id: int):
    row = EmotionAnalysis.query.filter_by(id=analysis_id, user_id=g.current_user.id).first()
    if not row:
        return jsonify({"error": "Analysis not found"}), 404
    return jsonify({"success": True, "analysis": _analysis_payload(row)})


@bp.patch("/analysis/<int:analysis_id>/notes")
@auth_required
def update_notes(analysis_id: int):
    row = EmotionAnalysis.query.filter_by(id=analysis_id, user_id=g.current_user.id).first()
    if not row:
        return jsonify({"error": "Analysis not found"}), 404

    data = request.get_json(silent=True) or {}
    mood = data.get("userReportedMood")
    reflection = data.get("personalReflection")

    note = AnalysisNote.query.filter_by(analysis_id=row.id, user_id=g.current_user.id).first()
    if not note:
        note = AnalysisNote(analysis_id=row.id, user_id=g.current_user.id)
        db.session.add(note)

    note.user_reported_mood = mood
    note.personal_reflection = reflection
    db.session.commit()
    return jsonify({"success": True, "analysis": _analysis_payload(row)})


@bp.delete("/analysis/<int:analysis_id>")
@auth_required
def delete_analysis(analysis_id: int):
    row = EmotionAnalysis.query.filter_by(id=analysis_id, user_id=g.current_user.id).first()
    if not row:
        return jsonify({"error": "Analysis not found"}), 404
    db.session.delete(row)
    db.session.commit()
    return jsonify({"success": True})


@bp.get("/history")
@auth_required
def list_history():
    query = EmotionAnalysis.query.filter_by(user_id=g.current_user.id)

    emotion = request.args.get("emotion")
    modality = request.args.get("modality")
    search = request.args.get("search")
    from_date = request.args.get("from")
    to_date = request.args.get("to")

    if emotion:
        query = query.filter(EmotionAnalysis.predicted_emotion == emotion)
    if modality in {"audio", "video"}:
        query = query.filter(EmotionAnalysis.modality == modality)
    if search:
        query = query.filter(EmotionAnalysis.predicted_emotion.ilike(f"%{search}%"))

    if from_date:
        try:
            dt = datetime.fromisoformat(from_date)
            query = query.filter(EmotionAnalysis.created_at >= dt)
        except ValueError:
            return jsonify({"error": "Invalid from date"}), 400
    if to_date:
        try:
            dt = datetime.fromisoformat(to_date)
            query = query.filter(EmotionAnalysis.created_at <= dt)
        except ValueError:
            return jsonify({"error": "Invalid to date"}), 400

    sort = request.args.get("sort", "created_at")
    order = request.args.get("order", "desc")
    sortable = {
        "created_at": EmotionAnalysis.created_at,
        "confidence": EmotionAnalysis.confidence_score,
        "emotion": EmotionAnalysis.predicted_emotion,
    }
    column = sortable.get(sort, EmotionAnalysis.created_at)
    query = query.order_by(column.desc() if order == "desc" else column.asc())

    page = max(1, int(request.args.get("page", 1)))
    per_page = min(100, max(1, int(request.args.get("perPage", 10))))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(
        {
            "success": True,
            "items": [_analysis_payload(x) for x in pagination.items],
            "pagination": {
                "page": page,
                "perPage": per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            },
        }
    )


@bp.get("/history/export")
@auth_required
def export_history():
    fmt = request.args.get("format", "csv")
    rows = (
        EmotionAnalysis.query.filter_by(user_id=g.current_user.id)
        .order_by(EmotionAnalysis.created_at.desc())
        .all()
    )

    if fmt == "json":
        return jsonify({"success": True, "items": [_analysis_payload(r) for r in rows]})

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "modality", "emotion", "confidence", "created_at"])
    for row in rows:
        writer.writerow([row.id, row.modality, row.predicted_emotion, row.confidence_score, row.created_at.isoformat()])
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=analysis-history.csv"},
    )


@bp.get("/analytics/summary")
@auth_required
def analytics_summary():
    q = EmotionAnalysis.query.filter_by(user_id=g.current_user.id)
    total = q.count()

    by_emotion = (
        db.session.query(EmotionAnalysis.predicted_emotion, func.count(EmotionAnalysis.id))
        .filter(EmotionAnalysis.user_id == g.current_user.id)
        .group_by(EmotionAnalysis.predicted_emotion)
        .all()
    )
    by_modality = (
        db.session.query(EmotionAnalysis.modality, func.count(EmotionAnalysis.id))
        .filter(EmotionAnalysis.user_id == g.current_user.id)
        .group_by(EmotionAnalysis.modality)
        .all()
    )
    by_day = (
        db.session.query(func.date(EmotionAnalysis.created_at), func.count(EmotionAnalysis.id))
        .filter(EmotionAnalysis.user_id == g.current_user.id)
        .group_by(func.date(EmotionAnalysis.created_at))
        .order_by(func.date(EmotionAnalysis.created_at).asc())
        .all()
    )

    return jsonify(
        {
            "success": True,
            "summary": {
                "totalAnalyses": total,
                "emotionDistribution": [{"emotion": e, "count": c} for e, c in by_emotion],
                "modalityBreakdown": [{"modality": m, "count": c} for m, c in by_modality],
                "activityOverTime": [{"date": str(d), "count": c} for d, c in by_day],
            },
        }
    )


@bp.get("/dashboard/summary")
@auth_required
def dashboard_summary():
    total = EmotionAnalysis.query.filter_by(user_id=g.current_user.id).count()
    recent = (
        EmotionAnalysis.query.filter_by(user_id=g.current_user.id)
        .order_by(EmotionAnalysis.created_at.desc())
        .limit(5)
        .all()
    )
    return jsonify(
        {
            "success": True,
            "summary": {
                "totalAnalyses": total,
                "recentActivity": [_analysis_payload(r) for r in recent],
            },
        }
    )
