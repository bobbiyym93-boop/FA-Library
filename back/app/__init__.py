from flask import Flask

from .config import Config
from .extensions import cors, db, migrate
from .routes.cases import cases_bp
from .routes.dashboard import dashboard_bp
from .routes.health import health_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(cases_bp, url_prefix="/api/v1/cases")
    app.register_blueprint(dashboard_bp, url_prefix="/api/v1/dashboard")

    return app
