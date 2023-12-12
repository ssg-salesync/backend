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
    if store_id is None:
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

