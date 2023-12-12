from flask import Blueprint, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import *
from models.models import db
from models.models import Categories, Items, Stores

bp = Blueprint('categories', __name__, url_prefix='/ca')

# 카테고리 조회
@bp.route('/stores/<store_id>/categories', methods=['GET'])
def get_category(store_id : int) :
    categories = Categories.query.filter(store_id == store_id).all()
    store = Stores.query.filter(store_id == store_id).first()
    
    print("categories: ", categories)
    print("stores: ", store)

    resp = {
        "categories": [
            {
                "id": categories.category_id,
                "name": categories.name
            }
        ],
        "store_id": store.store_id
    }

    return jsonify(resp)

# 카테고리 등록
@bp.route('/stores/<store_id>/categories', methods='POST')
@jwt_required()
def post_category(store_id : int) :
    req = request.get_json()
    
    store = Stores.query.filter(store_id=get_jwt_identity()).first()

    # jwt 권한 x
    if store.store_id != store_id:
        resp = {
            "result": "failed",
            "message": "카테고리 등록 권한 없음"
        }

        return jsonify(resp), 400

    new_category = Categories(
        name = req['name'],
        store_id = store.store_id
    )

    db.session.add(new_category)
    db.session.commit()


    resp = {
        "result": "success",
        "message": "카테고리 등록 성공",
        "category_id": new_category.category_id
    }

    return jsonify(resp), 200

# 카테고리 삭제
@bp.route('/stores/<store_id>/categories/<category_id>', methods=['DELETE'])
@jwt_required
def delete_category(store_id: int, category_id: int) :

    category = Categories.query.filter(category_id=category_id).first()
    store = Stores.query.filter(store_id=get_jwt_identity()).first()

    if category.store_id != store.store_id :
        resp = {
            "result" : "failed",
            "message" : "카테고리 삭제 권한 없음"
        }

        return jsonify(resp), 400

    db.session.delete(category)
    db.session.commit()

    resp = {
        "result" : "success",
        "message" : "카테고리 삭제 성공",
        "category_id" : category_id
    }

    return jsonify(resp), 200

# 품목 리스트 조회
@bp.route('/stores/<store_id>/items', methods=['GET'])
def get_item(store_id: int) :

    items = Items.query.filter(store_id=store_id).all()
    
    resp = {
        "items": [
            {
                "id" : items.item_id,
                "name" : items.name,
                "category_id": items.category_id,
                "price": items.price,
                "description": items.description
            }
        ]
    }

    return jsonify(resp), 200


#품목 등록
@bp.route('/stores/<store_id>/items', methods=['POST'])
@jwt_required
def post_item(store_id: int) :
    req = request.get_json()

    store = Stores.query.filter(store_id=get_jwt_identity()).first()

    # 등록 실패
    if store.store_id != store_id:
        resp = {
            "result" : "failed",
            "message" : "품목 등록 권한 없음"
        }
        return jsonify(resp), 400
    
    new_item = Items(name=req['name'], category_id=req['category_id'], price=req['price'], description=req['description'])

    db.session.add(new_item)
    db.session.commit()
    
    resp = {
        "result" : "success",
        "message" : "품목 등록 성공",
        "item_id" : new_item.item_id
    }

    return jsonify(resp), 200

# 품목 수정
@bp.route('/stores/<store_id>/items/<item_id>', methods=['PUT']) 
@jwt_required
def put_item(store_id : int, item_id : int) : 
    req = request.get_json()

    store = Stores.query.filter(store_id=get_jwt_identity()).first()

    # 품목 수정 실패
    if store.store_id != store_id:
        resp = {
            "result" : "failed",
            "message" : "품목 수정 권한 없음"
        }

        return jsonify(resp), 400
    
    item = Items.query.get(item_id).first()
    item.name = req['name']
    item.category_id = req['category_id']
    item.price = req['price']
    item.description = req['description']

    db.session.commit()
    
    resp = {
        "result" : "success",
        "message" : "품목 수정 성공", 
        "item_id" : item.item_id
    }

    return jsonify(resp), 200

# 품목 삭제
@bp.route('/stores/<store_id>/items/<item_id>', methods=['DELETE'])
@jwt_required
def delete_item(store_id: int, item_id: int) : 

    req = request.get_json()

    store = Stores.query.filter(store_id=get_jwt_identity()).first()

    # 품목 삭제 실패
    if store.store_id != store_id:
        resp = {
            "result" : "failed",
            "message" : "품목 삭제 권한 없음"
        }
        return jsonify(resp), 400
    
    item = Items.query.filter(item_id=item_id).first()

    db.session.delete(item)
    db.session.commit()

    resp = {
        "result" : "success",
        "message" : "품목 삭제 성공",
        "item_id" : item.item_id
    }

    return jsonify(resp), 200