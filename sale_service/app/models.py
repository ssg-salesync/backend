from . import db


class Sales(db.Model):
    sale_id = db.Column(db.Integer, primary_key=True)
    total_price = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime(), nullable=False)
    store_id = db.Column(db.Integer, nullable=False)
    payment_type = db.Column(db.String(200), nullable=False)