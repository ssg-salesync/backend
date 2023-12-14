from flask import Blueprint, request, jsonify
from models.models import db
from models.models import Categories, Items, Stores
from flask_cors import CORS
from flask_jwt_extended import *
import requests


bp = Blueprint('items', __name__, url_prefix='/categories')

# 품목 리스트 조회
@bp.route('/items', methods=['GET'])
@jwt_required()
def get_item() :

    store_id = get_jwt_identity()

    resp = []

    categories = Categories.query.filter_by(store_id=store_id).all()
    
    for category in categories:
        items = Items.query.filter_by(category_id=category.category_id).all()
        resp.append(items)

    for items in resp:
        print(items)
    
    
    return {
        "items": [
            {
                "id": item.item_id,
                "name": item.name,
                "category_id": item.category_id,
                "price": item.price,
                "description": item.description
            }
            for items in resp
            for item in items
        ]
    }, 200

# 품목 등록
@bp.route('/<category_id>/items', methods=['POST'])
@jwt_required()
def post_item(category_id: int):

    req = request.get_json()

    new_item = Items(name=req['name'], category_id=category_id, price=req['price'], description=req['description'])

    db.session.add(new_item)
    db.session.commit()

    return {
        "result": "success",
        "message": "품목 등록 성공",
        "id": new_item.item_id
    }, 200

# 품목 수정
@bp.route('/items/<item_id>', methods=['PUT'])
@jwt_required()
def put_item(item_id: int):
        
    req = request.get_json()
    print(req)

    edit_item = Items.query.filter_by(item_id=item_id).first()

    edit_item.name = req['name']
    edit_item.price = req['price']
    edit_item.description = req['description']

    db.session.commit()

    return {
        "result": "success",
        "message": "품목 수정 성공",
        "item_id": edit_item.item_id
    }, 200

# 품목 삭제
@bp.route('/items/<item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id: int):

    item = Items.query.filter_by(item_id=item_id).first()

    if item is None:
        return {
            "result": "failed",
            "message": '품목이 존재하지 않습니다.'
        }, 404
    
    db.session.delete(item)
    db.session.commit()

    return {
        "result": "success",
        "message": "품목 삭제 성공",
        "item_id": item.item_id
    }, 200