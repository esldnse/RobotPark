from flask import Flask
from app.extensions import db
from flask_migrate import Migrate
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)

    from app.routes.robots import bp as robots_bp
    from app.routes.mission_types import bp as mission_types_bp
    from app.routes.missions import bp as missions_bp
    from app.routes.reports import bp as reports_bp

    app.register_blueprint(robots_bp, url_prefix='/robots')
    app.register_blueprint(mission_types_bp, url_prefix='/mission_types')
    app.register_blueprint(missions_bp, url_prefix='/missions')
    app.register_blueprint(reports_bp, url_prefix='/reports')

    return app