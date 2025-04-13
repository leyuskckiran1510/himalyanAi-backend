from threading import Thread
from flask import Blueprint, Flask, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db, User, SummaryDb
from app.scraper import Summary, ai_summarize
from flask_cors import CORS
from flask import send_from_directory
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
            ipfs_hash = ipfsclient.add_json(summary_json)
            new_summary = SummaryDb(
                user_id=user_id,
                summary_id=ipfs_hash,
                full_url=full_url,
                site_domain=domain,
                created_at=one_day_ago_utc,
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

        Thread(target=upload_ipfs, args=(user_id, summary, domain, full_url), daemon=True).start()
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

def cat_ipfs_content(ipfs_hash):
    import requests
    
    url = f"http://localhost:5001/api/v0/cat?arg={ipfs_hash}"
    response = requests.post(url)  # Explicitly use POST method
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to retrieve content: {response.status_code} {response.text}")


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
    query = SummaryDb.query.filter_by(user_id=user_id)
    summaries = query.order_by(SummaryDb.created_at.desc()).all()

    # Create nested dictionary structure
    date_grouped = {}
    for s in summaries:
        date_str = s.created_at.strftime("%Y-%m-%d")
        
        # Initialize date if not exists
        if date_str not in date_grouped:
            date_grouped[date_str] = {}
        
        # Initialize domain if not exists
        if s.site_domain not in date_grouped[date_str]:
            date_grouped[date_str][s.site_domain] = {}
        
        try:
            summary_content = cat_ipfs_content(s.summary_id)
            try:
                # Try to parse as JSON
                summary_json = json.loads(summary_content)
                date_grouped[date_str][s.site_domain][s.full_url] = summary_json
            except (json.JSONDecodeError, TypeError):
                # If not valid JSON, use as string
                date_grouped[date_str][s.site_domain][s.full_url] = {"content": str(summary_content)}
        except Exception as e:
            # Handle IPFS retrieval errors
            date_grouped[date_str][s.site_domain][s.full_url] = {"error": f"Failed to retrieve content: {str(e)}"}
    from pprint import pprint
    pprint(date_grouped)

    # Sort dates in descending order (newest first)
    return jsonify(date_grouped), 200



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
                    "database_uri": current_app.config.get("SQLALCHEMY_DATABASE_URI", "").split("://")[0],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


