import datetime
from flask import Blueprint, jsonify, request, redirect
from models.models import db
from models.models import Sales, ItemsPerSale
from flask_bcrypt import *
from flask_jwt_extended import *
from flask_bcrypt import Bcrypt


bp = Blueprint('orders', __name__, url_prefix='/orders')

# 주문 조회
@bp.route('/', methods=['GET'])


# 주문 등록
@bp.route('/', methods=['POST'])
@jwt_required()
def post_order() :
    req = request.get_json()

    new_sale = Sales(total_price=req['total_price'], sale_date=datetime.datetime.now())

<<<<<<< Updated upstream
    db.session.add(new_sale)
    db.session.commit()
    
    for item in req['items'] :
        new_item_per_sale = ItemsPerSale(sale_id=new_sale.sale_id, item_id=item['item_id'], count=item['count'])
        db.session.add(new_item_per_sale)
        db.session.commit()

    return {
        "result": "success",
        "message": "주문 등록 성공",
        "id": new_sale.sale_id
    }, 201

# 주문 상세 조회
@bp.route('/<int:sale_id>', methods=['GET'])
@jwt_required()
def get_order(sale_id):
    sale = Sales.query.filter_by(sale_id=sale_id).first()
    items_per_sale = ItemsPerSale.query.filter_by(sale_id=sale_id).all()

    return {
        "result": "success",
        "message": "주문 상세 조회 성공",
        "sale": {
            "id": sale.sale_id,
            "total_price": sale.total_price,
            "sale_date": sale.sale_date
        },
        "items": [
            {
                "id": item_per_sale.item_id,
                "count": item_per_sale.count
            }
            for item_per_sale in items_per_sale
        ]
    }

# 주문 수정을 필요 없다고 생각함 -> 프론트에서 결제 전 최종적으로 수정된 값을 보내줌 
# 주문 수정
# @bp.route('/<int:sale_id>', methods=['PUT'])
# def put_order(sale_id: int) :
#     sale = Sales.query.filter_by(sale_id=sale_id).first()
#     items_per_sale = ItemsPerSale.query.filter_by(sale_id=sale_id).all()

#     if sale is None:
#         return {
#             "result": "failed",
#             "message": "주문 수정 실패"
#         }, 404

#     req = request.get_json()

#     sale.total_price = req['total_price']
#     sale.sale_date = datetime.datetime.now()

#     db.session.commit()

#     for item_per_sale in items_per_sale :
#         item_per_sale.count = req['items'][item_per_sale.item_id]['count']

#     return {
#         "result": "success",
#         "message": "주문 수정 성공"
#     }

# 주문 삭제
@bp.route('/<int:sale_id>', methods=['DELETE'])
@jwt_required()
def delete_order(sale_id: int):

    sale = Sales.query.filter_by(sale_id=sale_id).first()

    if sale is None:
        return {
            "result": "failed",
            "message": "주문 수정 실패"
        }, 404
=======
    existing_order = Orders.query.filter_by(table_no=table_no, paid=False).all()

    if existing_order:
        return jsonify({
            "result": "failed",
            "message": "신규 주문 등록 실패"
        }), 404
>>>>>>> Stashed changes

    db.session.query(Sales).filter_by(sale_id=sale_id).delete()

    db.session.commit()

<<<<<<< Updated upstream
    return {
=======
    return jsonify({
        "result": "success",
        "message": "결제 성공",
        "store_id": f"{store_id}",
        "table_no": table_no,
    }), 200


@bp.route('/', methods=['PUT'])
@jwt_required()
def get_order():
    store_id = get_jwt_identity()
    req = request.get_json()

    table_no = req['table_no']
    carts = req['carts']

    if not carts:
        db.session.delete(Orders.query.filter_by(table_no=table_no, paid=False).first())
        db.session.commit()
        return jsonify({
            "result": "success",
            "message": "주문 수정 성공"
        }), 200


    orders = Orders.query.filter_by(table_no=table_no, paid=False).all()
    print(orders, type(orders))

    if not orders:
        return jsonify({
            "result": "failed",
            "message": "존재하지 않는 주문"
        }), 404

    for order in orders:
        old_carts = Carts.query.filter_by(order_id=order.order_id).all()
        for old_cart in old_carts:
            db.session.delete(old_cart)
            db.session.commit()
        db.session.delete(order)
        db.session.commit()

    order = Orders(store_id=store_id, table_no=table_no, order_date=datetime.now(), paid=False)
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
        "message": "주문 수정 성공",
        "order_id": order.order_id,
        "table_no": order.table_no
    }), 200


@bp.route('/<table_no>', methods=['DELETE'])
@jwt_required()
def delete_order(table_no: int):

    orders = Orders.query.filter_by(table_no=table_no, paid=False).all()

    order_ids = []

    for order in orders:
        order_ids.append(order.order_id)
        db.session.delete(order)
        db.session.commit()

    return jsonify({
>>>>>>> Stashed changes
        "result": "success",
        "message": "주문 삭제 성공",
        "sale_id": sale_id
    }, 200