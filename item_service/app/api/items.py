from flask import Blueprint, request, jsonify
from ..models import db, Categories, Items
from flask_jwt_extended import *
from sqlalchemy import asc


bp = Blueprint('items', __name__, url_prefix='/categories')


# 품목 리스트 조회
@bp.route('/items', methods=['GET'])
@jwt_required()
def get_item():

    store_id = get_jwt_identity()

    categories = Categories.query.filter_by(store_id=store_id).order_by(asc(Categories.category_id)).all()

    resp = {"categories": []}

    for category in categories:
        items = Items.query.filter_by(category_id=category.category_id).order_by(asc(Items.item_id)).all()
        
        # 카테고리별 아이템 정보를 담을 딕셔너리
        category_data = {
            "category_id": category.category_id,
            "category_name": category.name,
            "items": []
        }

        for item in items:
            # 아이템 정보를 담을 딕셔너리
            item_data = {
                "item_id": item.item_id,
                "name": item.name,
                "price": item.price
            }
            category_data['items'].append(item_data)
        
        # 카테고리 정보를 리스트에 추가
        resp['categories'].append(category_data)
    
    return jsonify(resp), 200


# 품목 등록
@bp.route('/<category_id>/items', methods=['POST'])
@jwt_required()
def post_item(category_id: int):

    req = request.get_json()

    existing_item = Items.query.filter_by(name=req['name'], category_id=category_id).first()

    if existing_item:
        return {
            "result": "failed",
            "message": '존재하는 품목'
        }, 409

    new_item = Items(name=req['name'], category_id=category_id, price=req['price'])

    db.session.add(new_item)
    db.session.commit()

    return jsonify({
        "result": "success",
        "message": "품목 등록 성공",
        "id": new_item.item_id
    }), 201


# 품목 수정
@bp.route('/items/<item_id>', methods=['PUT'])
@jwt_required()
def put_item(item_id: int):
        
    req = request.get_json()

    edit_item = Items.query.filter_by(item_id=item_id).first()

    existing_item = Items.query.filter_by(name=req['name'], category_id=edit_item.category_id).first()


    edit_item.name = req['name']
    edit_item.price = req['price']

    db.session.commit()

    return jsonify({
        "result": "success",
        "message": "품목 수정 성공",
        "item_id": edit_item.item_id
    }), 200


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

    return jsonify({
        "result": "success",
        "message": "품목 삭제 성공",
        "item_id": item.item_id
    }), 200


@bp.route('/items/<item_id>', methods=['GET'])
def get_item_by_id(item_id: int):
    item = Items.query.filter_by(item_id=item_id).first()

    return jsonify({
        "result": "success",
        "message": "품목 조회 성공",
        "item": {
            "item_id": item.item_id,
            "name": item.name,
            "price": item.price
        }
    }), 200


@bp.route('/items/costs', methods=['GET'])
def get_cost():
    store_id = request.args.get('store_id')

    categories = Categories.query.filter_by(store_id=store_id).order_by(asc(Categories.category_id)).all()

    items = []

    for category in categories:
        items_per_category = Items.query.filter_by(category_id=category.category_id).order_by(asc(Items.item_id)).all()

        for item in items_per_category:
            items.append(item)


    return jsonify({
        "result": "success",
        "message": "원가 조회 성공",
        "items": [
            {
                "item_id": item.item_id,
                "name": item.name,
                "category_id": item.category_id,
                "price": item.price,
                "cost": item.cost
            }
            for item in items
        ]
    }), 200



@bp.route('/items/costs', methods=['POST'])
def post_cost():
    store_id = request.args.get('store_id')
    req = request.get_json()

    return_list = []

    for i in range(len(req['items'])):
        item = Items.query.filter_by(item_id=req['items'][i]['item_id']).first()
        item.cost = req['items'][i]['cost']
        db.session.commit()
        return_list.append(item)

    return jsonify({
        "result": "success",
        "message": "원가 등록 성공",
        "items": [
            {
                "item_id": item.item_id,
                "name": item.name,
                "category_id": item.category_id,
                "price": item.price,
                "cost": item.cost
            }
            for item in return_list
        ]
    }), 200


