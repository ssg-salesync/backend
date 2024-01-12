import json
import aiohttp
import asyncio
import os
from flask import Blueprint, request, jsonify
from ..models import db, ConsultingRequestIds
from flask_jwt_extended import *
import requests
import uuid
from ..kafka.producer import send_message


bp = Blueprint('consulting', __name__, url_prefix='/consulting')


@bp.route('/', methods=['GET'])
@jwt_required()
async def get_consulting():
    store_id = get_jwt_identity()
    req_id = str(uuid.uuid4())[:20]

    consulting_request_id = ConsultingRequestIds(store_id=store_id, req_id=req_id)

    db.session.add(consulting_request_id)
    db.session.commit()

    resp = requests.get("http://service-dash.default.svc.cluster.local/dashboard/sales").json()

    if resp.status_code != 200:
        return jsonify({
            "result": "failed",
            "message": "매출 조회 실패"
        }), 200

    sales_json = json.dumps(resp)
    prompt = (f'안녕하세요, 저는 소매점 운영자입니다. 저희 매장의 각 메뉴별 매출액, 순이익, 판매량을 포함한 JSON 데이터를 제공하고자 합니다. \
    이 데이터를 바탕으로 이익이 적게 나는 메뉴와 이익이 많이 나는 메뉴를 분석해주세요. 또한, 이 데이터를 통해 어떤 메뉴에 대한 프로모션 전략이 \
    매출 증대에 도움이 될지 구체적인 제안을 부탁드립니다. 추가적인 시장 분석이나 경쟁자 정보도 필요하다면 알려주세요. / {sales_json}')

    result = await send_prompt_to_gpt_async(req_id, prompt)
    # asyncio.run(send_prompt_to_gpt_async(req_id, prompt))

    # kafka 메시지 보내기 (producer)
    message = {'req_id': req_id, 'result': result}
    send_message("consulting", message)

    return jsonify({
        "req_id": req_id
    }), 200


async def send_prompt_to_gpt_async(req_id, prompt, engine='davinci'):
    req_id = req_id
    url = f"https://api.openai.com/v1/engines/{engine}/completions"

    headers = {
        "Authorization": f"Bearer {os.getenv('OPEN_AI_API_KEY')}",
        "Content-Type": "application/json"
    }

    data = {
        "prompt": prompt,
        "max_tokens": 500
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                return {
                    "response": await response.json()
                }
            else:
                return {
                    "error": await response.text()
                }

