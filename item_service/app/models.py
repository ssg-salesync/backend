from . import db


class Categories(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    store_id = db.Column(db.Integer, nullable=False)
    enabled = db.Column(db.Boolean, nullable=True, default=True)


class Items(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='CASCADE'), nullable=True)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    categories = db.relationship('Categories', backref=db.backref('item_set'))
    cost = db.Column(db.Integer, nullable=True)
    enabled = db.Column(db.Boolean, nullable=True, default=True)
