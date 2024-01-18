import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import *
from datetime import datetime, timedelta
import requests
import boto3


bp = Blueprint('bff', __name__, url_prefix='/')

baseUrl = "https://api.salesync.site"

sns_client = boto3.client(
    'sns',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name='ap-northeast-1'
)


@bp.route('/', methods=['GET'])
def main():
    return "Health Check"

@bp.route('/dashboard/sales', methods=['GET'])
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
        sale_resp = requests.get(f'{baseUrl}/sales/daily',
                                 params={'store_id': store_id, 'date': start}).json()
        # order service (order, cart) 에 해당하는 데이터 가져오기
        order_resp = requests.get(f'{baseUrl}/orders/daily',
                                  params={'store_id': store_id, 'date': start}).json()
        # item service (item, category) 에 해당하는 데이터 가져오기
        item_resp = requests.get(f'{baseUrl}/categories/items',
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
        sale_resp = requests.get(f'{baseUrl}/sales/period',
                                 params={'store_id': store_id, 'start': start, 'end': end}).json()
        # order service (order, cart) 에 해당하는 데이터 가져오기
        order_resp = requests.get(f'{baseUrl}/orders/period',
                                  params={'store_id': store_id, 'start': start, 'end': end}).json()
        # item service (item, category) 에 해당하는 데이터 가져오기
        item_resp = requests.get(f'{baseUrl}/categories/items',
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
        sales_resp = requests.get(f'{baseUrl}/sales/daily',
                                  params={'store_id': store_id, 'date': start}).json()
        order_resp = requests.get(f'{baseUrl}/orders/period',
                                  params={'store_id': store_id, 'start': start, 'end': end}).json()
        item_resp = requests.get(f'{baseUrl}/categories/items',
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

            sales_resp = requests.get(f'{baseUrl}/sales/daily',
                                      params={'store_id': store_id, 'date': date_str}).json()
            order_resp = requests.get(f'{baseUrl}/orders/period',
                                      params={'store_id': store_id, 'start': start_str, 'end': end_str}).json()
            item_resp = requests.get(f'{baseUrl}/categories/items',
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


@bp.route('/settlements', methods=['GET'])
@jwt_required()
def send_message():
    date = request.args.get('date')

    headers = {
        'Authorization': request.headers['Authorization'],
        'X-CSRF-TOKEN': request.headers['X-CSRF-TOKEN']
    }

    params = {
        'start': date,
        'end': date
    }

    store = requests.get(f"{baseUrl}/stores/", headers=headers).json()
    store_name = store['store']['store_name']
    owner_name = store['store']['owner_name']
    phone = store['store']['phone']

    sale = requests.get(f"{baseUrl}/dashboard/sales", headers=headers, params=params).json()
    sales_volume = sale['sales_volume']

    # message = f"안녕하세요. {owner_name}님, \n\n{date}의 {store_name} 총 매출은 {format(sales_volume, ',')}원입니다. \n\n감사합니다. "
    message = f"스마트한 AI 클라우드 POS에서 오늘의 총 매출을 알려드립니다. \n총 매출 : {format(sales_volume, ',')}원"


    sns_client.publish(
        PhoneNumber=f'+82{phone}',
        Message=message
    )

    return jsonify({
        "result": "success",
        "message": "정산 완료: 메시지 전송 완료"
    }), 200
