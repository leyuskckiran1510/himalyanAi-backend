from threading import Thread
from flask import Blueprint, Flask, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db, User, SummaryDb
from app.scraper import ai_summarize

bp = Blueprint("api", __name__)


@bp.route("/authenticate_or_identify", methods=["POST"])
def authenticate_or_identify():
    data = request.get_json()
    anon_hash = data.get("hash")

    if not anon_hash:
        return jsonify({"error": "Missing hash"}), 400

    user = User.query.filter_by(anon_hash=anon_hash).first()

    if not user:
        user = User(anon_hash=anon_hash)
        db.session.add(user)
        db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token}), 200


@bp.route("/summarize", methods=["POST"])
@jwt_required()
def summarize():
    data = request.get_json()
    text = data.get("content")
    summary = ai_summarize(text)
    return jsonify(summary.model_dump_json()), 200


@bp.route("/fetch_user_history", methods=["GET"])
@jwt_required()
def fetch_user_history():
    user_id = get_jwt_identity()
    summaries = SummaryDb.query.filter_by(user_id=user_id).order_by(SummaryDb.created_at.desc()).all()

    history = [
        {
            "date_of_creation": s.created_at.strftime("%Y-%m-%d"),
            "site_domain": s.site_domain,
            "full_url": s.full_url,
            "summary_id": s.summary_id,
        }
        for s in summaries
    ]

    return jsonify(history), 200
