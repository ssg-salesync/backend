from datetime import datetime
import requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import *
from ..models import db, Sales
from sqlalchemy import asc


bp = Blueprint('sales', __name__, url_prefix='/sales')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_sales():
    store_id = get_jwt_identity()

    sales = Sales.query.filter_by(store_id=store_id).order_by(asc(Sales.sale_date)).all()

    return jsonify({
        "sales": [
            {
                "id": sale.sale_id,
                "total_price": sale.total_price,
                "sale_date": sale.sale_date,
                "payment_type": sale.payment_type
            }
            for sale in sales
        ]
    }), 200


@bp.route('/', methods=['POST'])
@jwt_required()
def post_sale():
    store_id = get_jwt_identity()

    req = request.get_json()

    response = requests.put("http://service-order.default.svc.cluster.local/orders/paid",
                            json={"table_no": req['table_no'], "store_id": store_id})

    if response.status_code != 200:
        return jsonify({
            "result": "failed",
            "message": "결제 등록 실패"
        }), 200

    new_sale = Sales(
        total_price=req['total_price'],
        sale_date=datetime.now(),
        payment_type=req['payment_type'],
        store_id=store_id
    )

    db.session.add(new_sale)
    db.session.commit()

    return jsonify({
        "result": "success",
        "message": "결제 등록 성공",
        "id": new_sale.sale_id
    }), 201


@bp.route('/<int:sale_id>', methods=['DELETE'])
@jwt_required()
def delete_sale(sale_id: int):

    sale = Sales.query.filter_by(sale_id=sale_id).first()

    if not sale:
        return ({
            "result": "failed",
            "message": "존재하지 않는 결제 내역"
        }), 200

    db.session.query(Sales).filter_by(sale_id=sale_id).delete()
    db.session.commit()

    return jsonify({
        "result": "success",
        "message": "결제 취소 성공"
    }), 200


@bp.route('/daily', methods=['GET'])
def get_daily_sales():
    store_id = request.args.get('store_id')
    date = datetime.strptime(request.args.get('date'), '%Y-%m-%d').date()

    sales = Sales.query.filter_by(store_id=store_id).filter(
        db.func.date(Sales.sale_date) == date
    ).all()

    sales_volume = 0

    for sale in sales:
        sales_volume += sale.total_price

    return jsonify({
        "result": "success",
        "message": "하루 매출 조회 성공",
        "sales_volume": sales_volume,
        "date": date
    }), 200


@bp.route('/period', methods=['GET'])
def get_period_sales():
    store_id = request.args.get('store_id')
    start = datetime.strptime(request.args.get('start'), '%Y-%m-%d').date()
    end = datetime.strptime(request.args.get('end'), '%Y-%m-%d').date()

    sales = Sales.query.filter_by(store_id=store_id).filter(
        db.func.date(Sales.sale_date) >= start
    ).filter(
        db.func.date(Sales.sale_date) <= end
    ).all()

    sales_volume = 0

    for sale in sales:
        sales_volume += sale.total_price

    return jsonify({
        "result": "success",
        "message": "기간별 매출 조회 성공",
        "sales_volume": sales_volume,
        "start_date": start,
        "end_date": end
    }), 200

