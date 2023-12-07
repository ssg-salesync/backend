from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class stores(db.Model):
    store_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    owner_name = db.Column(db.String(20), nullalbe=False)
    phone = db.Column(db.String(20), nullable=False)
    store_name = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    store_type = db.Column(db.String(20), nullable=False)


class categories(db.Modle):
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullalbe=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.store_id', nullable=False))

class items(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullalbe=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='CASCADE', nullalbe=False))
    price = db.Column(db.Integer, nullalbe=False)
    description = db.Column(db.String(200), nullable=True)

class orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    is_procssing =db.Column(db.Boolean, nullable=True)
    cart_id =db.Column(db.Integer,db.ForeignKey('cart.cart_id', ondelete='CASCADE', nullable=False))

class carts(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Ingeger, db.ForeignKey('orders.order_id', ondelete='CASCADE', nullable=False))
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_uid', ondelete='CASECADE', nullable=False))
    quantity = db.Column(db.Integer, nullable=False)

class sales(db.Model):
    sale_id = db.Column(db.Integer, primary_key=True)
    total_price = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime(), nullalbe=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id', ondelete='CASCADE', nullable=False))
