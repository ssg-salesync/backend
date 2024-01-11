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

    response = requests.get("http://service-dash.default.svc.cluster.local/orders/paid", json={"table_no": req['table_no'], "store_id": store_id})

    return jsonify({
        "req_id": req_id
    }), 200




