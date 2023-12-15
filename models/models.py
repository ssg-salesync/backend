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
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    owner_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(200), nullable=False)
    store_name = db.Column(db.String(300), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    store_type = db.Column(db.String(200), nullable=False)


class Categories(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.store_id'), nullable=False)
    stores = db.relationship('Stores', backref=db.backref('category_set'))


class Items(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='CASCADE'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    categories = db.relationship('Categories', backref=db.backref('item_set'))


class Sales(db.Model):
    sale_id = db.Column(db.Integer, primary_key=True)
    total_price = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime(), nullable=False)


class ItemsPerSale(db.Model):
    items_per_sale_id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.sale_id', ondelete='CASCADE'), nullable=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id', ondelete='CASCADE'), nullable=True)
    count = db.Column(db.Integer, nullable=False)
    sales = db.relationship('Sales', backref=db.backref('items_per_sale_set'))
    items = db.relationship('Items', backref=db.backref('items_per_sale_set'))

