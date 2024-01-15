import json
import aiohttp
import os
from flask import Blueprint, jsonify, request
from ..models import db, ConsultingResults
from flask_jwt_extended import *
import requests
import uuid
from ..kafka.producer import send_message
import openai
import asyncio


bp = Blueprint('consulting', __name__, url_prefix='/consulting')


@bp.route('/', methods=['GET'])
@jwt_required()
async def get_consulting():
    # store_id = get_jwt_identity()
    req_id = str(uuid.uuid4())[:20]

    headers = {
        'Authorization': request.headers['Authorization'],
        'X-CSRF-Token': request.headers['X-CSRF-Token']
    }

    params = {
        'start': request.args.get('start'),
        'end': request.args.get('end')
    }

    # req_id를 db 저장
    consulting_result = ConsultingResults(req_id=req_id)
    db.session.add(consulting_result)
    db.session.commit()

    resp = requests.get("http://service-dash.default.svc.cluster.local/dashboard/sales", headers=headers, params=params)

    if resp.status_code != 200:
        return jsonify({
            "result": "failed",
            "message": "매출 조회 실패"
        }), 200

    sales_json = json.dumps(resp.json())
    prompt = (f'안녕하세요, 저는 소매점 운영자입니다. 저희 매장의 각 메뉴별 매출액, 순이익, 판매량을 포함한 JSON 데이터를 제공하고자 합니다. \
    이 데이터를 바탕으로 이익이 적게 나는 메뉴와 이익이 많이 나는 메뉴를 분석해주세요. 또한, 이 데이터를 통해 어떤 메뉴에 대한 프로모션 전략이 \
    매출 증대에 도움이 될지 구체적인 제안을 부탁드립니다. 추가적인 시장 분석이나 경쟁자 정보도 필요하다면 알려주세요. / {sales_json}')

    await send_prompt_to_gpt_async(req_id, prompt)

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


async def send_prompt_to_gpt_async(req_id, prompt, engine='davinci'):
    openai.api_key = os.getenv('OPEN_AI_API_KEY')

    try:
        response = await asyncio.to_thread(
            openai.Completion.create,
            engine=engine,
            prompt=prompt,
            max_tokens=150
        )

        # 응답 처리
        text = response.choices[0].text.strip()

        save_response_to_db(req_id, text)

    except Exception as e:
        print(f"Error while sending prompt to GPT: {e}")


def save_response_to_db(req_id, response_text):
    consulting_result = ConsultingResults.query.filter_by(req_id=req_id).first()
    consulting_result.response = response_text
    consulting_result.is_completed = True
    db.session.commit()

    message = {';req_id': req_id, 'response': response_text}
    send_message('consulting', message)
