from flask import Blueprint, request, jsonify
from ..models import db, ConsultingRequestIds
from flask_jwt_extended import *
import requests
import uuid


bp = Blueprint('consulting', __name__, url_prefix='/consulting')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_consulting():
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

    return jsonify({
        "req_id": req_id
    }), 200
