from flask import Blueprint, jsonify, request, redirect
from models.models import db
from models.models import Stores
from flask_bcrypt import *
from flask_jwt_extended import *
from flask_wtf.csrf import generate_csrf
from flask_bcrypt import Bcrypt


bp = Blueprint('orders', __name__, url_prefix='/orders')

