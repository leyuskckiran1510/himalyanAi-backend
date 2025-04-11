from app import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    anon_hash = db.Column(db.String(128), unique=True, nullable=False)


class SummaryDb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    summary_id = db.Column(db.String(128), nullable=False)
    full_url = db.Column(db.String(512))
    site_domain = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
