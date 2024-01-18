from . import db


class Stores(db.Model):
    store_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    owner_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(200), nullable=False)
    store_name = db.Column(db.String(300), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    store_type = db.Column(db.String(200), nullable=False)
