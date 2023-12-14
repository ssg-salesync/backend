from flask import Blueprint, request, jsonify
from models.models import db
from models.models import Categories, Items, Stores
from flask_cors import CORS
from flask_jwt_extended import *


bp = Blueprint('categories', __name__, url_prefix='/stores')

# 카테고리 조회
@bp.route('/<store_id>/categories', methods=['GET'])
def get_category(store_id : int) :

    categories = Categories.query.filter_by(store_id=store_id).all()

    return {
        "categories" : [
            {
                "id": category.category_id,
                "name": category.name
            }
            for category in categories
        ],
        "store_id": store_id
    }


# 카테고리 등록
# @bp.route('/<store_id>/categories', methods='POST')
# @jwt_required()
# def post_category(store_id:int):
#     req = request.get_json()
#     name = req['name']
    
#     return "post categories" + name
# def post_category(store_id : int) :
#     req = request.get_json()
    
#     store = Stores.query.filter(store_id=get_jwt_identity()).first()

#     # jwt 권한 x
#     if store.store_id != store_id:
#         resp = {
#             "result": "failed",
#             "message": "카테고리 등록 권한 없음"
#         }

#         return jsonify(resp), 400

#     new_category = Categories(
#         name = req['name'],
#         store_id = store.store_id
#     )

#     db.session.add(new_category)
#     db.session.commit()


#     resp = {
#         "result": "success",
#         "message": "카테고리 등록 성공",
#         "category_id": new_category.category_id
#     }

#     return jsonify(resp), 200

# # 카테고리 삭제
# @bp.route('/<store_id>/categories/<category_id>', methods=['DELETE'])
# @jwt_required
# def delete_category(store_id: int, category_id: int) :

#     category = Categories.query.filter(category_id=category_id).first()
#     store = Stores.query.filter(store_id=get_jwt_identity()).first()

#     if category.store_id != store.store_id :
#         resp = {
#             "result" : "failed",
#             "message" : "카테고리 삭제 권한 없음"
#         }

#         return jsonify(resp), 400

#     db.session.delete(category)
#     db.session.commit()

#     resp = {
#         "result" : "success",
#         "message" : "카테고리 삭제 성공",
#         "category_id" : category_id
#     }

#     return jsonify(resp), 200

# 품목 리스트 조회
@bp.route('/<store_id>/items', methods=['GET'])
def get_item(store_id: int) :
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



# #품목 등록
# @bp.route('/<store_id>/items', methods=['POST'])
# @jwt_required
# def post_item(store_id: int) :
#     req = request.get_json()

#     store = Stores.query.filter(store_id=get_jwt_identity()).first()

#     # 등록 실패
#     if store.store_id != store_id:
#         resp = {
#             "result" : "failed",
#             "message" : "품목 등록 권한 없음"
#         }
#         return jsonify(resp), 400
    
#     new_item = Items(name=req['name'], category_id=req['category_id'], price=req['price'], description=req['description'])

#     db.session.add(new_item)
#     db.session.commit()
    
#     resp = {
#         "result" : "success",
#         "message" : "품목 등록 성공",
#         "item_id" : new_item.item_id
#     }

#     return jsonify(resp), 200

# # 품목 수정
# @bp.route('/<store_id>/items/<item_id>', methods=['PUT']) 
# @jwt_required
# def put_item(store_id : int, item_id : int) : 
#     req = request.get_json()

#     store = Stores.query.filter(store_id=get_jwt_identity()).first()

#     # 품목 수정 실패
#     if store.store_id != store_id:
#         resp = {
#             "result" : "failed",
#             "message" : "품목 수정 권한 없음"
#         }

#         return jsonify(resp), 400
    
#     item = Items.query.get(item_id).first()
#     item.name = req['name']
#     item.category_id = req['category_id']
#     item.price = req['price']
#     item.description = req['description']

#     db.session.commit()
    
#     resp = {
#         "result" : "success",
#         "message" : "품목 수정 성공", 
#         "item_id" : item.item_id
#     }

#     return jsonify(resp), 200

# # 품목 삭제
# @bp.route('/stores/<store_id>/items/<item_id>', methods=['DELETE'])
# @jwt_required
# def delete_item(store_id: int, item_id: int) : 

#     req = request.get_json()

#     store = Stores.query.filter(store_id=get_jwt_identity()).first()

#     # 품목 삭제 실패
#     if store.store_id != store_id:
#         resp = {
#             "result" : "failed",
#             "message" : "품목 삭제 권한 없음"
#         }
#         return jsonify(resp), 400
    
#     item = Items.query.filter(item_id=item_id).first()

#     db.session.delete(item)
#     db.session.commit()

#     resp = {
#         "result" : "success",
#         "message" : "품목 삭제 성공",
#         "item_id" : item.item_id
#     }

#     return jsonify(resp), 200