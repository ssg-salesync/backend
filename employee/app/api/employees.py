from flask import Blueprint, request, jsonify
from models.models import db
from flask_jwt_extended import *


bp = Blueprint('employees', __name__, url_prefix='/employees')
