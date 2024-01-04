from flask import Blueprint, request, jsonify
import requests
import xmltodict
from datetime import datetime

bp = Blueprint('weather', __name__, url_prefix='/weather')

@bp.route('/', methods=['GET'])
def getweather():

    currnet_date = datetime.now()

    date = currnet_date.date().strftime("%Y%m%d")
    time = currnet_date.time().strftime("%H%M")

    response = requests.get(f'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst?ServiceKey=itjde0Gu8qwR%2FBOyEoxWD1L%2Fy6FmbK8E34wGcdGVxNRFNhe4v4NNAeMONUDFyChoKf6ih14CugCbreFwp4fbpg%3D%3D&numOfRows=10&pageNo=1&base_date={date}&base_time={time}&nx=54&ny=124')

    json_date = xmltodict.parse(response.text)


    return jsonify(json_date), 200