from flask import Blueprint, request, jsonify
from models.models import db
from models.models import Categories
from flask_jwt_extended import *

bp = Blueprint('main', __name__, url_prefix='/')


# 카테고리 조회
@bp.route('/', methods=['GET'])
def main():
    return "Hello World!"