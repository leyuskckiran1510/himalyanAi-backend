from threading import Thread
from flask import Blueprint, Flask, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db, User, SummaryDb
from app.scraper import Summary, ai_summarize
from flask_cors import CORS
from app import ipfsclient
from datetime import datetime
import json
from app import get_app
from datetime import timedelta

one_day_ago_utc = datetime.utcnow() - timedelta(days=2)

bp = Blueprint("api", __name__)
CORS(bp)


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


def upload_ipfs(user_id, summary, domain, full_url):
    with get_app().app_context():
        try:

            summary_json = summary.model_dump_json()
            print(summary_json)
            ipfs_hash = ipfsclient.add_json(summary_json)

            print(
                {
                    "user_id": user_id,
                    "summary_id": ipfs_hash,
                    "full_url": full_url,
                    "site_domain": domain,
                }
            )

            new_summary = SummaryDb(
                user_id=user_id,
                summary_id=ipfs_hash,
                full_url=full_url,
                site_domain=domain,
                created_at= one_day_ago_utc,
                
            )

            db.session.add(new_summary)
            db.session.commit()

            return True
        except Exception as e:
            print(f"Error saving to IPFS/database: {str(e)}")
            db.session.rollback()
            return False


@bp.route("/summarize", methods=["POST"])
@jwt_required()
def summarize():
    data = request.get_json()

    text = data.get("content")
    domain = data.get("url")
    full_url = data.get("full")

    try:
        summary = ai_summarize(text)
        user_id = get_jwt_identity()

        Thread(
            target=upload_ipfs, args=(user_id, summary, domain, full_url), daemon=True
        ).start()
        return jsonify(summary.model_dump()), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "error": True,
                    "summary": "",
                    "notes": [],
                    "references": [],
                    "error_msg": f"Failed to process content: {str(e)}",
                }
            ),
            500,
        )


@bp.route("/discard", methods=["POST"])
@jwt_required()
def discard():
    data = request.get_json()
    full_url = data.get("of")
    uid = get_jwt_identity()
    SummaryDb.query.filter_by(user_id=uid, full_url=full_url).delete()
    db.session.commit()
    return jsonify({"msg": f"[{full_url}]: summary history discarded. "}), 200


@bp.route("/fetch_user_history", methods=["GET"])
@jwt_required()
def fetch_user_history():
    user_id = get_jwt_identity()
    date_param = request.args.get("date")

    query = SummaryDb.query.filter_by(user_id=user_id)
    if date_param:
        try:
            target_date = datetime.strptime(date_param, "%Y-%m-%d").date()

            query = query.filter(db.func.date(SummaryDb.created_at) == target_date)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    summaries = query.order_by(SummaryDb.created_at.desc()).all()

    if not summaries and date_param:
        return jsonify({"message": f"No summaries found for date {date_param}"}), 404

    date_grouped = {}
    for s in summaries:
        date_str = s.created_at.strftime("%Y-%m-%d")
        if date_str not in date_grouped:
            date_grouped[date_str] = []

        date_grouped[date_str].append(
            {
                "summary_id": s.summary_id,
                "full_url": s.full_url,
                "site_domain": s.site_domain,
                "created_at": s.created_at.isoformat(),
            }
        )

    result = [
        {"date": date, "summaries": summaries}
        for date, summaries in date_grouped.items()
    ]

    return jsonify(result), 200


@bp.route("/date_summaries", methods=["GET"])
@jwt_required()
def date_summaries():
    user_id = get_jwt_identity()
    date_param = request.args.get("date")

    if not date_param:
        return (
            jsonify({"error": "Date parameter is required (format: YYYY-MM-DD)"}),
            400,
        )

    try:
        target_date = datetime.strptime(date_param, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    summaries = (
        SummaryDb.query.filter_by(user_id=user_id)
        .filter(db.func.date(SummaryDb.created_at) == target_date)
        .order_by(SummaryDb.created_at.desc())
        .all()
    )

    if not summaries:
        return jsonify({"message": f"No summaries found for {date_param}"}), 404

    result = {date_param: {}}

    for summary in summaries:
        domain = summary.site_domain
        if domain not in result[date_param]:
            result[date_param][domain] = {}

        try:
            summary_content = ipfsclient.cat(summary.summary_id)
            try:
                summary_json = json.loads(summary_content)
                result[date_param][domain][summary.full_url] = summary_json
            except json.JSONDecodeError:
                result[date_param][domain][summary.full_url] = str(summary_content)
        except Exception as e:
            result[date_param][domain][summary.full_url] = {
                "error": f"Failed to retrieve content: {str(e)}"
            }

    return jsonify(result), 200


@bp.route("/db_health", methods=["GET"])
def db_health():
    """Endpoint to check if the database is working properly"""
    try:
        db.session.execute(db.select(User).limit(1))
        user_count = db.session.query(db.func.count(User.id)).scalar()
        summary_count = db.session.query(db.func.count(SummaryDb.id)).scalar()

        return (
            jsonify(
                {
                    "status": "healthy",
                    "user_count": user_count,
                    "summary_count": summary_count,
                    "database_uri": current_app.config.get(
                        "SQLALCHEMY_DATABASE_URI", ""
                    ).split("://")[0],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500
