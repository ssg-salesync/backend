from flask import Blueprint, request, jsonify, logging
from flask_jwt_extended import *
from ..kafka.consumer import consume_message
from datetime import datetime, timedelta
import requests
import threading

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('/costs', methods=['GET'])
@jwt_required()
def get_costs():
    store_id = get_jwt_identity()

    return (requests.get(f'http://service-item.default.svc.cluster.local/categories/items/costs?store_id={store_id}')
            .json())


@bp.route('/costs', methods=['POST'])
@jwt_required()
def post_costs():
    store_id = get_jwt_identity()
    req = request.get_json()

    return (requests.post(
        f'http://service-item.default.svc.cluster.local/categories/items/costs?store_id={store_id}', json=req)
            .json())


@bp.route('/costs/<item_id>', methods=['PUT'])
@jwt_required()
def put_costs(item_id: int):
    req = request.get_json()

    return requests.put(f'http://service-item.default.svc.cluster.local/categories/items/costs/{item_id}',
                        json=req).json()


# 전체 매출 기간별 조회 (아이템별 분류)
@bp.route('/sales', methods=['GET'])
@jwt_required()
def get_sale_per_category():
    store_id = get_jwt_identity()
    start = request.args.get('start')
    end = request.args.get('end')

    headers = {
        'Authorization': request.headers['Authorization'],
        'X-CSRF-TOKEN': request.headers['X-CSRF-TOKEN']
    }

    if start == end:
        # sale service (sale) 에 해당하는 데이터 가져오기
        sale_resp = requests.get(f'http://service-sale.default.svc.cluster.local/sales/daily',
                                 params={'store_id': store_id, 'date': start}).json()
        # order service (order, cart) 에 해당하는 데이터 가져오기
        order_resp = requests.get(f'http://service-order.default.svc.cluster.local/orders/daily',
                                  params={'store_id': store_id, 'date': start}).json()
        # item service (item, category) 에 해당하는 데이터 가져오기
        item_resp = requests.get(f'http://service-item.default.svc.cluster.local/categories/items',
                                 headers=headers, params={'store_id': store_id}).json()

        items = get_items_in_orders(order_resp, item_resp)

        return jsonify({
            "result": "success",
            "message": "매출 조회 성공",
            "start_date": start,
            "end_date": end,
            "sales_volume": sale_resp['sales_volume'],
            "items": items
        }), 200
    else:
        # sale service (sale) 에 해당하는 데이터 가져오기
        sale_resp = requests.get(f'http://service-sale.default.svc.cluster.local/sales/period',
                                 params={'store_id': store_id, 'start': start, 'end': end}).json()
        # order service (order, cart) 에 해당하는 데이터 가져오기
        order_resp = requests.get(f'http://service-order.default.svc.cluster.local/orders/period',
                                  params={'store_id': store_id, 'start': start, 'end': end}).json()
        # item service (item, category) 에 해당하는 데이터 가져오기
        item_resp = requests.get(f'http://service-item.default.svc.cluster.local/categories/items',
                                 headers=headers, params={'store_id': store_id}).json()

        items = get_items_in_orders(order_resp, item_resp)

        return jsonify({
            "result": "success",
            "message": "매출 조회 성공",
            "start_date": start,
            "end_date": end,
            "sales_volume": sale_resp['sales_volume'],
            "items": items
        }), 200


@bp.route('/volumes', methods=['GET'])
@jwt_required()
def get_total_volumes():
    store_id = get_jwt_identity()
    start = request.args.get('start')
    end = request.args.get('end')

    headers = {
        'Authorization': request.headers['Authorization'],
        'X-CSRF-TOKEN': request.headers['X-CSRF-TOKEN']
    }

    if start == end:
        sales_resp = requests.get(f'http://service-sale.default.svc.cluster.local/sales/daily',
                                  params={'store_id': store_id, 'date': start}).json()
        order_resp = requests.get(f'http://service-order.default.svc.cluster.local/orders/period',
                                  params={'store_id': store_id, 'start': start, 'end': end}).json()
        item_resp = requests.get(f'http://service-item.default.svc.cluster.local/categories/items',
                                 headers=headers, params={'store_id': store_id}).json()

        items = get_items_in_orders(order_resp, item_resp)
        profit = 0

        for item in items:
            profit += item['profit']

        sales_volume = sales_resp['sales_volume']

        return jsonify({
            "total": [
                {
                    "date": start,
                    "profit": profit,
                    "sales_volume": sales_volume
                }
            ],
            "message": "기간별 매출 조회 성공",
            "result": "success",
            "start_date": start,
            "end_date": end
        }), 200
    else:
        total = []
        start = datetime.strptime(start, '%Y-%m-%d')
        end = datetime.strptime(end, '%Y-%m-%d')

        for i in range(int((end - start).days) + 1):
            date = start + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            start_str = start.strftime('%Y-%m-%d')
            end_str = end.strftime('%Y-%m-%d')

            sales_resp = requests.get(f'http://service-sale.default.svc.cluster.local/sales/daily',
                                      params={'store_id': store_id, 'date': date_str}).json()
            order_resp = requests.get(f'http://service-order.default.svc.cluster.local/orders/period',
                                      params={'store_id': store_id, 'start': start_str, 'end': end_str}).json()
            item_resp = requests.get(f'http://service-item.default.svc.cluster.local/categories/items',
                                     headers=headers, params={'store_id': store_id}).json()

            items = get_items_in_orders(order_resp, item_resp)
            profit = 0

            for item in items:
                profit += item['profit']

            sales_volume = sales_resp['sales_volume']

            total.append({
                "date": date.strftime('%Y-%m-%d'),
                "profit": profit,
                "sales_volume": sales_volume
            })

        return jsonify({
            "total": total,
            "message": "기간별 매출 조회 성공",
            "result": "success",
            "start_date": start,
            "end_date": end
        }), 200


def get_items_in_orders(order_resp, item_resp):
    item_quantities = {}
    for order in order_resp['orders']:
        for cart in order['carts']:
            item_id = cart['item_id']
            quantity = cart['quantity']

            if item_id in item_quantities:
                item_quantities[item_id] += quantity
            else:
                item_quantities[item_id] = quantity

    items_data = {}
    for category in item_resp['categories']:
        for item in category['items']:
            items_data[item['item_id']] = item

    items = []
    for item_id, quantity in item_quantities.items():
        if item_id in items_data:
            if items_data[item_id]['cost'] is None:
                items_data[item_id]['cost'] = 0
            items.append({
                "item_id": item_id,
                "name": items_data[item_id]['name'],
                "sales_volume": items_data[item_id]['price'] * quantity,
                "profit": items_data[item_id]['price'] * quantity - items_data[item_id]['cost'] * quantity,
                "quantity": quantity
            })
        else:
            pass

    return items


@bp.route('/consulting/<req_id>', methods=['GET'])
def get_consulting(req_id):
    message = consume_message('consulting', req_id)

    return jsonify({
        "result": "success",
        "message": "상담 요청 조회 성공",
        "consulting": message
    }), 200

@bp.route('/consulting/test/<req_id>', methods=['GET'])
def test_get_consulting(req_id):
    message = consume_message('test', req_id)

    return jsonify({
        "result": "success",
        "message": "상담 요청 조회 성공",
        "consulting": message
    }), 200
