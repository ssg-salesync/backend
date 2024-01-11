from flask import Blueprint, request, jsonify
from ..models import db, ConsultingResults
from flask_jwt_extended import *
import uuid


bp = Blueprint('consulting', __name__, url_prefix='/consulting')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_consulting():
    store_id = get_jwt_identity()
