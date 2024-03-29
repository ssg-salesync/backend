from flask import Blueprint, request, jsonify
from flask_jwt_extended import *
from datetime import datetime, timedelta
import requests


bp = Blueprint('bff', __name__, url_prefix='/bff')

baseUrl = "https://api.salesync.site"


@bp.route('/sales', methods=['GET'])
@jwt_required()
def get_bff_sale_per_category():
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
def get_bff_total_volumes():
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

# 원가 조회
@bp.route('/costs', methods=['GET'])
@jwt_required()
def get_bff_cost():
    try:
        store_id = get_jwt_identity()

        res = requests.get(f'{baseUrl}/categories/items/costs',
                                    params={'store_id': store_id}).json()

        # 변환된 데이터를 담을 빈 리스트
        transformed_data = []

        # 각 항목을 순회하며 새로운 형식으로 변환
        for item in res['items']:
            category_id = item['category_id']
            category_name = item['category_name']
            item_info = {
                'name': item['name'],
                'price': item['price'],
                'cost': item['cost'],
                'item_id': item['item_id']
            }

            # 해당 카테고리가 이미 결과에 있는지 확인
            category_found = False
            for category in transformed_data:
                if category['category_id'] == category_id:
                    category['items'].append(item_info)
                    category_found = True
                    break

            # 해당 카테고리가 결과에 없으면 새로운 카테고리 추가
            if not category_found:
                new_category = {
                    'category_id': category_id,
                    'category_name': category_name,
                    'items': [item_info]
                }
                transformed_data.append(new_category)

            # 최종 결과 출력
            print(transformed_data)

        return jsonify({
                "result": "success",
                "message": "원가 조회 성공",
                "items": transformed_data
        }), 200
    except Exception as e:
        return jsonify({"error": "내부 서버 오류"}),500

@bp.route('/costs', methods=['POST'])
def post_cost():
    try:
        req = request.get_json()
        return_list = []

        headers = {
            'Authorization': request.headers['Authorization'],
            'X-CSRF-TOKEN': request.headers['X-CSRF-TOKEN']
        }

        print("req['items']" ,req['items'])
        print("=====================")
        newData = []

        for category in req['items']:
            category_id = category["category_id"]
            category_name = category["category_name"]

            for item in category["items"]:
                transformed_item = {
                    "item_id": item["item_id"],
                    # "name": item["name"],
                    # "category_id": category_id,
                    # "category_name": category_name,
                    # "price": item["price"],
                    "cost": item["cost"]
                }
                newData.append(transformed_item)
        print("newData", newData)
        returnData = {'items':newData}
        print("===========")
        print("returnData", returnData)
        
        res = requests.post(f'{baseUrl}/dashboard/costs', headers=headers,
                                        json = returnData ).json()
        print("=================")
        print("res",res)

        return jsonify(res), 200
    except Exception as e :
        return jsonify({"error": str(e)})