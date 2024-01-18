from . import db


class ConsultingResults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    req_id = db.Column(db.String(20), nullable=False)
    result = db.Column(db.JSON, nullable=True)
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
