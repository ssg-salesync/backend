from . import db


class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    paid = db.Column(db.Boolean, nullable=False, default=False)
    order_date = db.Column(db.DateTime(), nullable=False)
    store_id = db.Column(db.Integer, nullable=False)
    table_no = db.Column(db.Integer, nullable=False)


class Carts(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=True)
    item_id = db.Column(db.Integer, nullable=True)
    orders = db.relationship('Orders', backref=db.backref('cart_set'))
    quantity = db.Column(db.Integer, nullable=False, default=1)
