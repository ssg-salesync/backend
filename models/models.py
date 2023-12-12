from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))


class Stores(db.Model):
    store_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    owner_name = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    store_name = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    store_type = db.Column(db.String(20), nullable=False)


class Categories(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.store_id'), nullable=False)


class Items(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='CASCADE'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=True)


class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    is_processing = db.Column(db.Boolean, nullable=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.cart_id', ondelete='CASCADE'), nullable=False)


class Carts(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id', ondelete='CASCADE'), nullable=False)


class Sales(db.Model):
    sale_id = db.Column(db.Integer, primary_key=True)
    total_price = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime(), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False)
