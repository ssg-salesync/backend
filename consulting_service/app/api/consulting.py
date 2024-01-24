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

    result = ConsultingResults.query.filter_by(req_id='a7d9a66e-2c18-40b3-a').first()
    message = {'req_id': 'a7d9a66e-2c18-40b3-a', 'response': result['result']}
    send_message("demo", message)


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

