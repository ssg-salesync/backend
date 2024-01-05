from datetime import datetime
import requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import *
from ..models import db, Orders, Carts
import requests
import xmltodict


bp = Blueprint('orders', __name__, url_prefix='/orders')


@bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    store_id = get_jwt_identity()
    req = request.get_json()

    table_no = req['table_no']
    carts = req['carts']

    if not carts:
        return jsonify({
            "result": "failed",
            "message": "주문 등록 실패 : 주문 내역 없음"
        }), 200


    order = Orders(store_id=store_id, table_no=table_no, order_date=datetime.now(), paid=False)
    db.session.add(order)
    db.session.commit()

    for cart in carts:
        item_id = cart['item_id']
        quantity = cart['quantity']

        cart = Carts(order_id=order.order_id, item_id=item_id, quantity=quantity)
        db.session.add(cart)
        db.session.commit()

    return jsonify({
        "result": "success",
        "message": "주문 생성 성공",
        "order_id": order.order_id,
        "table_no": order.table_no
    }), 200


@bp.route('/unpaids', methods=['GET'])
@jwt_required()
def get_unpaids():
    store_id = get_jwt_identity()
    orders = db.session.query(Orders).filter_by(store_id=store_id, paid=False).all()
    cart_in_order = get_carts_in_order(orders)

    return jsonify({
        "result": "success",
        "message": "미결제 주문 목록 조회 성공",
        "store_id": f"{store_id}",
        "orders": cart_in_order
    }), 200


@bp.route('/unpaids/<int:table_no>', methods=['GET'])
@jwt_required()
def get_unpaids_by_table(table_no: int):
    store_id = get_jwt_identity()
    order = db.session.query(Orders).filter_by(store_id=store_id, paid=False, table_no=table_no).first()

    if order is None:
        return jsonify({
           "carts": []
        }), 200

    carts = db.session.query(Carts).filter_by(order_id=order.order_id).all()
    cart_in_order, total_price = get_items_in_cart(carts)

    return jsonify({
        "result": "success",
        "message": "미결제 주문 테이블 조회 성공",
        "store_id": f"{store_id}",
        "order_id": order.order_id,
        "table_no": order.table_no,
        "total_price": total_price,
        "carts": cart_in_order
    }), 200


@bp.route('/paid', methods=['PUT'])
def pay():
    req = request.get_json()
    store_id = req['store_id']
    table_no = req['table_no']

    orders = db.session.query(Orders).filter_by(store_id=store_id, table_no=table_no, paid=False).all()

    if not orders:
        return jsonify({
            "result": "failed",
            "message": "결제 실패 : 존재하지 않는 주문"
        }), 400

    for order in orders:
        order.paid = True

    db.session.commit()

    return jsonify({
        "result": "success",
        "message": "결제 성공",
        "store_id": f"{store_id}",
        "table_no": table_no,
    }), 200


@bp.route('/', methods=['PUT'])
@jwt_required()
def get_order():
    store_id = get_jwt_identity()
    req = request.get_json()

    table_no = req['table_no']
    carts = req['carts']

    if not carts:
        old_order = Orders.query.filter_by(table_no=table_no, paid=False).first()

        if old_order:
            db.session.delete(old_order)
            db.session.commit()

            return jsonify({
                "result": "cancelled",
                "message": "주문 취소 : 주문 내역 없음"
            }), 200

        return jsonify({
            "result": "failed",
            "message": "존재하지 않는 주문"
        }), 200

    order = Orders.query.filter_by(table_no=table_no, paid=False).first()

    old_carts = Carts.query.filter_by(order_id=order.order_id).all()

    for old_cart in old_carts:
        db.session.delete(old_cart)
        db.session.commit()

    for cart in carts:
        item_id = cart['item_id']
        quantity = cart['quantity']

        cart = Carts(order_id=order.order_id, item_id=item_id, quantity=quantity)
        db.session.add(cart)
        db.session.commit()

    return jsonify({
        "result": "success",
        "message": "주문 수정 성공",
        "order_id": order.order_id,
        "table_no": order.table_no
    }), 200


@bp.route('/<table_no>', methods=['DELETE'])
@jwt_required()
def delete_order(table_no: int):

    orders = Orders.query.filter_by(table_no=table_no, paid=False).all()

    order_ids = []

    for order in orders:
        order_ids.append(order.order_id)
        db.session.delete(order)
        db.session.commit()

    return jsonify({
        "result": "success",
        "message": "주문 삭제 성공",
        "table_no": table_no,
        "orders": order_ids
    }), 200


@bp.route('/weather', methods=['GET'])
def get_weather():
    values = {
        'POP': '강수확률',
        'PTY': '강수형태',
        'PCP': '1시간 강수량',
        'REH': '습도',
        'SNO': '1시간 신적설',
        'SKY': '하늘상태',
        'TMP': '1시간 기온',
        'TMN': '일 최저기온',
        'TMX': '일 최고기온',
        'UUU': '풍속(동서성분)',
        'VVV': '풍속(남북성분)',
        'WAV': '파고',
        'VEC': '풍향',
        'WSD': '풍속',
        'T1H': '기온',
        'RN1': '1시간 강수량',
        'SKY': '하늘상태',
        'LGT': '낙뢰',
    }

    current_date = datetime.now()

    date = current_date.date().strftime("%Y%m%d")
    time = current_date.time().strftime("%H%M")

    response = requests.get(f'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst?ServiceKey=itjde0Gu8qwR%2FBOyEoxWD1L%2Fy6FmbK8E34wGcdGVxNRFNhe4v4NNAeMONUDFyChoKf6ih14CugCbreFwp4fbpg%3D%3D&numOfRows=10&pageNo=1&base_date={date}&base_time=0800&nx=54&ny=124')

    json_date = xmltodict.parse(response.text)
    items = []

    for i in range(len(json_date['response']['body']['items']['item'])):
        search_value = [values.get(key, []) for key in values.keys() if key == json_date['response']['body']['items']['item'][i]['category']]
        obsr_value = [json_date['response']['body']['items']['item'][i]['obsrValue']]
        item = [search_value[0], obsr_value[0]]
        items.append(item)


    return jsonify({
        "result": "success",
        "message": "날씨 조회 성공",
        "items": [
            {
                "category": item[0],
                "obsrValue": item[1]
            }
            for item in items
        ]
    }), 200


def get_carts_in_order(orders):
    cart_in_order = {}

    for order in orders:
        if order.table_no not in cart_in_order:
            cart_in_order[order.table_no] = {
                "order_id": order.order_id,
                "order_date": order.order_date,
                "table_no": order.table_no,
                "total_price": 0,
                "carts": []
            }

        carts = Carts.query.filter(Carts.order_id == order.order_id).all()
        items_in_cart, total_price = get_items_in_cart(carts)

        cart_in_order[order.table_no]["total_price"] += total_price

        for item in items_in_cart:
            existing_item = next((i for i in cart_in_order[order.table_no]["carts"] if i['item_id'] == item['item_id']), None)

            if existing_item:
                existing_item['quantity'] += item['quantity']
            else:
                cart_in_order[order.table_no]["carts"].append({
                    "item_id": item["item_id"],
                    "item_name": item["item_name"],
                    "quantity": item["quantity"]
                })

    result = list(cart_in_order.values())
    return result


def get_items_in_cart(carts):
    items_in_cart = []
    total_price = 0

    item_quantity_mapping = {}

    for cart in carts:
        item_id = cart.item_id
        quantity = cart.quantity

        if item_id not in item_quantity_mapping:
            item_quantity_mapping[item_id] = 0

        item_quantity_mapping[item_id] += quantity

    for item_id, quantity in item_quantity_mapping.items():
        try:
            response = requests.get(f'http://service-item.default.svc.cluster.local/categories/items/{item_id}')
            response.raise_for_status()
            item = response.json()['item']

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP Error: {http_err}")
            continue

        except requests.exceptions.RequestException as request_err:
            print(f"Request Error: {request_err}")
            continue

        except requests.exceptions.JSONDecodeError as json_err:
            print(f"JSON Decode Error: {json_err}")
            continue

        items_in_cart.append({'item_id': item_id, 'item_name': item['name'], 'quantity': quantity})
        total_price += (item['price'] * quantity)

    return items_in_cart, total_price
