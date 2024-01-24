from flask import Blueprint, jsonify, request, current_app
from ..models import db, ConsultingResults
from flask_jwt_extended import *
from ..kafka.producer import send_message
from openai import OpenAI

import asyncio
import requests
import uuid
import json
import os
import threading


bp = Blueprint('consulting', __name__, url_prefix='/consulting')
client = OpenAI(api_key=os.environ['OPEN_AI_API_KEY'])


@bp.route('/', methods=['GET'])
@jwt_required()
async def get_consulting():
    req_id = str(uuid.uuid4())[:20]

    headers = {
        'Authorization': request.headers['Authorization'],
        'X-CSRF-Token': request.headers['X-CSRF-Token']
    }

    params = {
        'start': request.args.get('start'),
        'end': request.args.get('end')
    }

    consulting_result = ConsultingResults(req_id=req_id)
    db.session.add(consulting_result)
    db.session.commit()

    resp = requests.get("http://service-dash.default.svc.cluster.local/dashboard/sales", headers=headers, params=params)
    # resp = requests.get("https://api.salesync.site/dashboard/sales", headers=headers, params=params)

    if resp.status_code != 200:
        return jsonify({
            "result": "failed",
            "message": "매출 조회 실패"
        }), 200

    sales_json = json.dumps(resp.json())
    prompt = f'너는 지금부터 비즈니스 컨설턴트야. 너는 소매점의 프로모션 전략을 세워줄거야.업로드한 파일을 매출과 원가를 고려해서 순이익을 계산하여, 어떤 메뉴가 이익이 나지 않는지, 어떤 메뉴에서 이익이 많이 나는지를 찾아서 전체적인 프로모션을 세워줘. 예를 들어, 어느 메뉴에서 어떤 홍보나 이벤트를 진행하면 매출이 증가할 수 있을지와 같은 전략을 자세하게 세워줘. 데이터라는 말 대신 매출 정보라는 말을 사용해주고, 핵심 내용만 이야기해줘. / {sales_json}'

    app = current_app._get_current_object()
    threading.Thread(target=run_async_task, args=(app, req_id, prompt)).start()

    return jsonify({
        "req_id": req_id
    }), 200


@bp.route('/<req_id>', methods=['GET'])
def get_check_consulting(req_id):
    consulting_result = ConsultingResults.query.filter_by(req_id=req_id).first()

    if consulting_result is None:
        return jsonify({
            "result": "failed",
            "message": "컨설팅 요청 없음"
        }), 200
    elif consulting_result.is_completed is False:
        return jsonify({
            "result": "not completed",
            "message": "컨설팅 진행 중"
        }), 200
    else:
        return jsonify({
            "result": "success",
            "message": "컨설팅 완료",
            "req_id": req_id
        }), 200


def run_async_task(app, req_id, prompt):
    with app.app_context():
        asyncio.run(send_prompt_to_gpt_async(req_id, prompt))


async def async_chat_completion(engine, prompt):
    return client.chat.completions.create(
        model=engine,
        messages=[{
            "role": "user",
            "content": prompt
            }
        ]
    )


async def send_prompt_to_gpt_async(req_id, prompt, engine='gpt-3.5-turbo'):
    try:
        response = await asyncio.to_thread(
            lambda: asyncio.run(async_chat_completion(engine, prompt))
        )

        save_response_to_db(req_id, response.choices[0].message.content)

    except Exception as e:
        print(f"Error while sending prompt to GPT: {e}")


def save_response_to_db(req_id, response_text):
    consulting_result = ConsultingResults.query.filter_by(req_id=req_id).first()
    consulting_result.result = response_text
    consulting_result.is_completed = True
    db.session.commit()

    message = {'req_id': req_id, 'response': response_text}
    send_message('consulting', message)



@bp.route('/test', methods=['GET'])
@jwt_required()
def test():

    consulting_result = ConsultingResults(req_id='a7d9a66e-2c18-40b3-a')
    db.session.add(consulting_result)
    db.session.commit()

    response_text = "컨설팅\n\n분석 결과에 따르면, 가장 많은 순이익을 낸 상위 메뉴는 다음과 같습니다:\n\n포테이토 피자: 총 매출액 231,000원, 총 원가 23,100원, 총 순이익 137,700원\n페퍼로니 피자: 총 매출액 168,000원, 총 원가 19,800원, 총 순이익 148,200원\n오븐스파게티: 총 매출액 75,000원, 총 원가 7,500원, 총 순이익 67,500원\n케이준포테이토: 총 매출액 72,000원, 총 원가 7,200원, 총 순이익 64,800원\n치즈 크러스트: 총 매출액 48,000원, 총 원가 6,200원, 총 순이익 41,800원\n\n이 데이터를 바탕으로 프로모션 전략을 제안하겠습니다:\n\n프로모션 전략 제안\n\n1. 포테이토 피자 프로모션 강화\n- 전략: 포테이토 피자는 높은 순이익을 창출하므로, 이를 중심으로 프로모션 활동을 강화합니다.\n\n실행: \'포테이토 피자 주문 시 음료 무료 제공\' 이벤트를 진행하여 매출 증대를 도모합니다. 이는 포테이토 피자의 판매를 촉진하고, 음료와 함께 주문을 유도하여 고객 만족도를 높일 수 있습니다.\n2. 페퍼로니 피자 주간 특별 할인\n- 전략: 페퍼로니 피자의 좋은 순이익을 활용하여 매출을 증가시킵니다.\n- 실행: \'페퍼로니 피자 주간\'을 마련하여 특정 요일에 할인된 가격으로 페퍼로니 피자를 제공합니다. 이는 특별 이벤트로 고객의 관심을 끌고, 대량 주문을 유도할 수 있습니다.\n3. 오븐스파게티와 케이준포테이토 결합 프로모션\n- 전략: 두 메뉴의 순이익을 활용하여 결합 판매를 촉진합니다.\n- 실행: \n'오븐스파게티 + 케이준포테이토 콤보 할인\'을 통해 두 메뉴를 함께 구매할 경우 할인을 제공합니다. 이는 각 메뉴의 매력을 높이고, 고객에게 다양한 맛을 제공하여 매출 증가에 기여합n니다.\n4. 소셜 미디어 캠페인 및 온라인 마케팅\n- 전략: 인기 메뉴를 중심으로 소셜 미디어 캠페인을 통해 브랜드 인지도를 높이고, 새로운 고객을 유치합니다.\n- 실행: 인스타그램, 페이스북 등에서 \'포토 콘테스트\'를 진행합니다. 고객이 인기 메뉴와 함께 찍은 사진을 업로드하고, 가장 좋아요를 많이 받은 고객에게는 무료 식사 쿠폰을 제공합니다. 이는 고객 참여를 유도하고, SNS를 통한 입소문 마케팅을 강화합니다.\n\n추가 전략\n- 시즌별 테마 메뉴 개발: 계절이나 특정 기념일에 맞춰 특별 메뉴를 개발하여 한정 판매합니다. 이는 신선함을 제공하고, 특별한 날에 방문을 유도할 수 있습니다.\n- 멤버십 프로그램 도입: 단골 고객을 위한 멤버십 프로그램을 마련하여, 충성도 높은 고객에게 포인트 적립이나 특별 할인 혜택을 제공합니다. 이는 장기적인 고객 관계 구축에 도움이 됩니다.\n\n각 전략은 해당 소매점의 고객층, 위치, 경쟁 환경 등을 고려하여 조정할 수 있습니다. "
    message = {'req_id': 'a7d9a66e-2c18-40b3-a', 'response': response_text}
    send_message("test", message)

    consulting_result = ConsultingResults.query.filter_by(req_id='a7d9a66e-2c18-40b3-a').first()
    consulting_result.result = response_text
    consulting_result.is_completed = True
    db.session.commit()

    return jsonify({
        "req_id": "a7d9a66e-2c18-40b3-a"
    }), 200


global_integer = 0

@bp.route('/test/<req_id>', methods=['GET'])
def test_check_consulting(req_id):
    global global_integer
    if global_integer == 3:
        global_integer = 0
        return jsonify({
            "result": "success",
            "message": "컨설팅 완료",
            "req_id": req_id
        }), 200
    else:
        global_integer += 1
        return jsonify({
            "result": "not completed",
            "message": "컨설팅 진행 중"
        }), 200

