from flask import Flask
from config import Config
from app.extensions import mail

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # project blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.log import bp as log_bp
    app.register_blueprint(log_bp, url_prefix='/log')

    from app.suggestions import bp as suggestions_bp
    app.register_blueprint(suggestions_bp, url_prefix='/suggestions')

    from app.about import bp as about_bp
    app.register_blueprint(about_bp, url_prefix='/about')

    mail.init_app(app)

    return app
