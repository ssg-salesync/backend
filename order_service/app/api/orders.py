from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from models.models import db
from models.models import Sales, ItemsPerSale
from flask_jwt_extended import *


bp = Blueprint('orders', __name__, url_prefix='/orders')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    store_id = get_jwt_identity()
    sales = Sales.query.filter_by(store_id=store_id).all()

    return jsonify({
        "result": "success",
        "message": "주문 목록 조회 성공",
        "store_id": f"{store_id}",
        "sales": [
            {
                "id": sale.sale_id,
                "total_price": sale.total_price,
                "sale_date": sale.sale_date
            }
            for sale in sales
        ]
    }), 200


@bp.route('/by_period', methods=['GET'])
@jwt_required()
def get_orders_by_period():
    period = request.args.get('period', type=int, default=1)

    start_date = datetime.now() - timedelta(days=period)

    store_id = get_jwt_identity()
    sales = Sales.query.filter(
        (Sales.store_id == store_id) & (Sales.sale_date >= start_date)
    ).all()

    return jsonify({
        "result": "success",
        "message": "기간별 주문 목록 조회 성공",
        "store_id": f"{store_id}",
        "period": f"{period}일",
        "sales": [
            {
                "id": sale.sale_id,
                "total_price": sale.total_price,
                "sale_date": sale.sale_date
            }
            for sale in sales
        ]
    }), 200


@bp.route('/by_date', methods=['GET'])
@jwt_required()
def get_orders_by_date():
    date = request.args.get('date', type=str, default=datetime.now().strftime('%Y-%m-%d'))
    store_id = get_jwt_identity()
    sales = Sales.query.filter(Sales.store_id == store_id).all()
    daily_sales = []

    for sale in sales:
        if date in str(sale.sale_date):
            daily_sales.append(sale)

    return jsonify({
        "result": "success",
        "message": "일별 주문 목록 조회 성공",
        "store_id": f"{store_id}",
        "date": f"{date}",
        "sales": [
            {
                "id": sale.sale_id,
                "total_price": sale.total_price,
                "sale_date": sale.sale_date
            }
            for sale in daily_sales
        ]
    }), 200


# 주문 등록
@bp.route('/', methods=['POST', 'OPTIONS'])
@jwt_required()
def post_order():
    req = request.get_json()
    store_id = get_jwt_identity()
    new_sale = Sales(total_price=req['total_price'], sale_date=datetime.now(), store_id=store_id)

    db.session.add(new_sale)
    db.session.commit()
    
    for item in req['items']:
        new_item_per_sale = ItemsPerSale(sale_id=new_sale.sale_id, item_id=item['item_id'], count=item['count'])
        db.session.add(new_item_per_sale)
        db.session.commit()

    return jsonify({
        "result": "success",
        "message": "주문 등록 성공",
        "id": new_sale.sale_id
    }), 201


# 주문 상세 조회
@bp.route('/<int:sale_id>', methods=['GET'])
@jwt_required()
def get_order(sale_id):
    sale = Sales.query.filter_by(sale_id=sale_id).first()
    items_per_sale = ItemsPerSale.query.filter_by(sale_id=sale_id).all()

    return jsonify({
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
    }), 200


# 주문 삭제
@bp.route('/<int:sale_id>', methods=['DELETE'])
@jwt_required()
def delete_order(sale_id: int):

    sale = Sales.query.filter_by(sale_id=sale_id).first()

    if sale is None:
        return jsonify({
            "result": "failed",
            "message": "주문 삭제 실패"
        }), 404

    db.session.query(Sales).filter_by(sale_id=sale_id).delete()
    db.session.commit()

    return jsonify({
        "result": "success",
        "message": "주문 삭제 성공",
        "sale_id": sale_id
    }), 200
