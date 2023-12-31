from flask import Blueprint, request
from flask_jwt_extended import *
import requests


bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('/costs', methods=['GET'])
@jwt_required()
def get_costs():
    store_id = get_jwt_identity()

    return requests.get(f'http://service-item.default.svc.cluster.local/categories/items/costs?store_id={store_id}').json()


@bp.route('/costs', methods=['POST'])
@jwt_required()
def post_costs():
    store_id = get_jwt_identity()
    req = request.get_json()

    return requests.post(f'http://service-item.default.svc.cluster.local/categories/items/costs?store_id={store_id}', json=req).json()


@bp.route('/costs/<item_id>', methods=['PUT'])
@jwt_required()
def put_costs(item_id: int):
    req = request.get_json()

    return requests.put(f'http://service-item.default.svc.cluster.local/categories/items/costs/{item_id}', json=req).json()


@bp.route('/daily-sales', methods=['GET'])
@jwt_required()
def get_sales_per_date():
    store_id = get_jwt_identity()
    date = request.args.get('date')

    return requests.get(f'http://service-order.default.svc.cluster.local/orders/daily', params={'store_id': store_id, 'date': date}).json()