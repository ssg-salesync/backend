from . import db


class ConsultingResults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, nullable=False)
    req_id = db.Column(db.String(20), nullable=False)
    long_text = db.Column(db.Text)
