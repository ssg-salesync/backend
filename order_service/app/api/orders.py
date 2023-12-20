from flask import Blueprint, jsonify, request
from models.models import db
from flask_jwt_extended import *
from models.models import Orders, Carts, Items


bp = Blueprint('orders', __name__, url_prefix='/orders')


@bp.route('/unpaids', methods=['GET'])
@jwt_required()
def get_unpaids():
    store_id = get_jwt_identity()
    orders = Orders.query.filter((Orders.store_id == store_id) & (Orders.paid is False)).all()
    cart_in_order = get_carts_in_order(orders)

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
    order = Orders.query.filter((Orders.store_id == store_id) & (Orders.paid is False) & (Orders.table_no == table_no)).first()
    carts = Carts.query.filter(Carts.order_id == order.order_id).all()
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

    return cart_in_order


def get_items_in_cart(carts):
    items_in_cart = []
    total_price = 0

    for cart in carts:
        item = Items.query.filter(Items.item_id == cart.item_id).first()
        items_in_cart.append({'item_id': item.item_id, 'item_name': item.name})
        total_price += item.price

    return items_in_cart, total_price
