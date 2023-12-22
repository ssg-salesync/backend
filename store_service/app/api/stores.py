from flask import Blueprint, jsonify, request
from ..models import db, Stores
from flask_bcrypt import *
from flask_jwt_extended import *
from flask_wtf.csrf import generate_csrf
from flask_bcrypt import Bcrypt


bp = Blueprint('stores', __name__, url_prefix='/stores')
bcrypt = Bcrypt()


@bp.route('/', methods=['GET'])
def get_stores():
    stores = Stores.query.all()

    return jsonify({
        "stores": [
            {
                "id": store.store_id,
                "username": store.username,
                "owner_name": store.owner_name,
                "phone": store.phone,
                "store_name": store.store_name,
                "address": store.address,
                "store_type": store.store_type
            }
            for store in stores
        ]
    }), 200


@bp.route('/', methods=['POST'])
def create_store():
    data = request.get_json()

    username = data['username']
    password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    owner_name = data['owner_name']
    phone = data['phone']
    store_name = data['store_name']
    address = data['address']
    store_type = data['store_type']

    store = Stores(username=username, password=password, owner_name=owner_name, phone=phone, store_name=store_name,
                   address=address, store_type=store_type)
    db.session.add(store)
    db.session.commit()

    return jsonify({
        "store": {
            "store_id": store.store_id,
            "username": store.username,
            "owner_name": store.owner_name,
            "phone": store.phone,
            "store_name": store.store_name,
            "address": store.address,
            "store_type": store.store_type
        },
        "result": "success",
        "message": "매장 등록 성공"
    }), 201


@bp.route('/<int:store_id>', methods=['GET'])
def get_store(store_id):
    store = Stores.query.get(store_id)
    return jsonify({
        "store": {
            "store_id": store.store_id,
            "username": store.username,
            "owner_name": store.owner_name,
            "phone": store.phone,
            "store_name": store.store_name,
            "address": store.address,
            "store_type": store.store_type
        }
    }), 200


@bp.route('/<int:store_id>', methods=['PUT'])
def update_store(store_id):
    store = Stores.query.get(store_id)
    data = request.get_json()

    store.username = data['username']
    store.password = generate_password_hash(data['password']).decode('utf-8')
    store.owner_name = data['owner_name']
    store.phone = data['phone']
    store.store_name = data['store_name']
    store.address = data['address']
    store.store_type = data['store_type']

    db.session.commit()

    return jsonify({
        "store": {
            "store_id": store.store_id,
            "username": store.username,
            "owner_name": store.owner_name,
            "phone": store.phone,
            "store_name": store.store_name,
            "address": store.address,
            "store_type": store.store_type
        }
    }), 200


@bp.route('/<int:store_id>', methods=['DELETE'])
def delete_store(store_id):
    store = Stores.query.get(store_id)
    db.session.delete(store)
    db.session.commit()

    return jsonify({
        "result": "success",
        "message": "매장 삭제 성공"
    }), 200


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    store = Stores.query.filter_by(username=username).first()

    if not store or not bcrypt.check_password_hash(pw_hash=store.password, password=password):
        return jsonify({'error': 'Invalid username or password'}), 400

    access_token = create_access_token(identity=store.store_id)

    return jsonify({
        'result': "success",
        "store_id": store.store_id,
        "access_token": access_token,
        "csrf_token": generate_csrf()
    }), 200


@bp.route('/check', methods=['GET'])
def check_username():
    username = request.args.get('username')
    store = Stores.query.filter_by(username=username).first()

    if store:
        return jsonify({
            "result": "failed",
            "message": "이미 존재하는 아이디입니다."
        }), 200
    else:
        return jsonify({
            "result": "success",
            "message": "사용 가능한 아이디입니다."
        }), 200