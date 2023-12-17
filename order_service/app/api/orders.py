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

    db.session.query(Sales).filter_by(sale_id=sale_id).delete()

    db.session.commit()

    return {
        "result": "success",
        "message": "주문 삭제 성공",
        "sale_id": sale_id
    }, 200