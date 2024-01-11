from flask import Blueprint, request, jsonify
from ..models import db, Categories
from flask_jwt_extended import *
from sqlalchemy import asc


bp = Blueprint('categories', __name__, url_prefix='/categories')


# 카테고리 조회
@bp.route('/', methods=['GET'])
@jwt_required()
def get_category():
    store_id = get_jwt_identity()
    categories = Categories.query.filter_by(store_id=store_id, enabled=True).order_by(asc(Categories.category_id)).all()

    return jsonify({
        "categories": [
            {
                "id": category.category_id,
                "name": category.name
            }
            for category in categories
        ],
        "store_id": store_id
    }), 200


# 카테고리 등록
@bp.route('/', methods=['POST'])
@jwt_required()
def post_category():
    store_id = get_jwt_identity()
    req = request.get_json()
    existing_category = Categories.query.filter_by(name=req['name'], store_id=store_id, enabled=True).first()

    if existing_category:
        return {
            "result": "failed",
            "message": '존재하는 카테고리'
        }, 409

    new_category = Categories(
        name=req['name'],
        store_id=store_id
    )

    db.session.add(new_category)
    db.session.commit()

    return jsonify({
        "result": "success",
        "message": "카테고리 등록 성공",
        "id": new_category.category_id
    }), 201


# 카테고리 수정
@bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
def put_category(category_id: int):
    store_id = get_jwt_identity()
    category = Categories.query.filter_by(category_id=category_id).first()

    if category is None:
        return {
            "result": "failed",
            "message": '존재하지 않는 카테고리.'
        }, 404

    req = request.get_json()
    existing_category = Categories.query.filter_by(name=req['name'], store_id=store_id, enabled=True).first()

    if existing_category:
        return {
            "result": "failed",
            "message": '존재하는 카테고리'
        }, 409

    category.name = req['name']
    db.session.commit()

    return jsonify({
        "result": "success",
        "message": "카테고리 수정 성공",
        "id": category_id
    }), 201


# 카테고리 삭제
@bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id: int):
    category = Categories.query.filter_by(category_id=category_id).first()

    if category is None:
        return {
            "result": "failed",
            "message": '카테고리가 존재하지 않습니다.'
        }, 404

    category.enabled = False
    db.session.commit()

    return jsonify({
        "result": "success",
        "message": "카테고리 삭제 성공",
        "category_id": category_id
    }), 200
