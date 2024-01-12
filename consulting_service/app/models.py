from . import db


class ConsultingRequestIds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, nullable=False)
    req_id = db.Column(db.String(20), nullable=False)


class ConsultingResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    req_id = db.Column(db.String(20), nullable=False)
    result = db.Column(db.JSON, nullable=True)
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
