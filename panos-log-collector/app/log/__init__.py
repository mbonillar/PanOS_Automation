from flask import Blueprint

bp = Blueprint('log', __name__)

from app.log import routes
