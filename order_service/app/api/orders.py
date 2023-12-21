from flask import Blueprint, jsonify, request
from models.models import db
from flask_jwt_extended import *
from models.models import Orders, Carts, Items
from datetime


bp = Blueprint('orders', __name__, url_prefix='/orders')


@bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    store_id = get_jwt_identity()
    req = request.get_json()

    table_no = req['table_no']
    carts = req['carts']

    order = Orders(store_id=store_id, table_no=table_no, order_date=datetime.datetime.now(), paid=False)
    db.session.add(order)
    db.session.commit()

    for cart in carts:
        item_id = cart['item_id']
        quantity = cart['quantity']

        cart = Carts(order_id=order.order_id, item_id=item_id, quantity=quantity)
        db.session.add(cart)
        db.session.commit()

    return jsonify({
        "result": "success",
        "message": "주문 생성 성공",
        "order_id": order.order_id,
        "table_no": order.table_no
    }), 200


@bp.route('/unpaids', methods=['GET'])
@jwt_required()
def get_unpaids():
    store_id = get_jwt_identity()
    orders = db.session.query(Orders).filter_by(store_id=store_id, paid=False).all()
    cart_in_order = get_carts_in_order(orders)

    print(cart_in_order)

    return jsonify({
        "result": "success",
        "message": "미결제 주문 목록 조회 성공",
        "store_id": f"{store_id}",
        "orders": cart_in_order
    }), 200


@bp.route('/unpaids/<int:table_no>', methods=['GET'])
@jwt_required()
def get_unpaids_by_table(table_no: int):
    store_id = get_jwt_identity()
    order = db.session.query(Orders).filter_by(store_id=store_id, paid=False, table_no=table_no).first()
    carts = db.session.query(Carts).filter_by(order_id=order.order_id).all()
    cart_in_order, total_price = get_items_in_cart(carts)

    return jsonify({
        "result": "success",
        "message": "미결제 주문 테이블 조회 성공",
        "store_id": f"{store_id}",
        "order_id": order.order_id,
        "table_no": order.table_no,
        "total_price": total_price,
        "carts": cart_in_order
    }), 200


def get_carts_in_order(orders):
    cart_in_order = []

    for order in orders:
        carts = Carts.query.filter(Carts.order_id == order.order_id).all()
        items_in_cart, total_price = get_items_in_cart(carts)

        cart_in_order.append({
            "order_id": order.order_id,
            "order_date": order.order_date,
            "table_no": order.table_no,
            "total_price": total_price,
            "carts": items_in_cart
        })

    print(orders)
    return cart_in_order


def get_items_in_cart(carts):
    items_in_cart = []
    total_price = 0

    for cart in carts:
        item = Items.query.filter(Items.item_id == cart.item_id).first()
        items_in_cart.append({'item_id': item.item_id, 'item_name': item.name, 'quantity': cart.quantity})
        total_price += (item.price * cart.quantity)

    return items_in_cart, total_price
