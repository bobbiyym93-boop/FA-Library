from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from app.extensions import db


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return {"code": error.code, "message": error.description, "data": None}, error.code

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        db.session.rollback()
        current_app.logger.exception("database operation failed", exc_info=error)
        return {"code": 5001, "message": "database operation failed", "data": None}, 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        db.session.rollback()
        current_app.logger.exception("unexpected server error", exc_info=error)
        return {"code": 5000, "message": "internal server error", "data": None}, 500
