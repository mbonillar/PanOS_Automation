from app.main import bp
from flask import render_template


@bp.route('/')
def index():
    return render_template('index.html')


@bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 400


@bp.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
