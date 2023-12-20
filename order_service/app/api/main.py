from flask import Blueprint

bp = Blueprint('main', __name__, url_prefix='/')


# 카테고리 조회
@bp.route('/', methods=['GET'])
def main():
    return "Hello World!"