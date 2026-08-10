from flask import Blueprint
from sqlalchemy import func

from app.extensions import db
from app.models import Case


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/statistics")
def statistics():
    products = db.session.query(Case.product, func.count(Case.id)).group_by(Case.product).all()
    projects = db.session.query(Case.project, func.count(Case.id)).group_by(Case.project).all()
    return {
        "code": 0,
        "message": "success",
        "data": {
            "total_cases": db.session.query(func.count(Case.id)).scalar(),
            "product_distribution": [{"name": name, "value": count} for name, count in products],
            "cases_by_project": [{"name": name, "value": count} for name, count in projects],
        },
    }
