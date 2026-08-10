from flask import Blueprint, request
from sqlalchemy import or_

from app.extensions import db
from app.models import Case
from app.schemas.case_schema import CASE_FIELDS, validate_case_payload
from app.services.case_service import generate_case_id
from app.services.data_dictionary_service import grouped_options


cases_bp = Blueprint("cases", __name__)
def response(data=None, message="success", code=0, status=200):
    return {"code": code, "message": message, "data": data}, status


@cases_bp.get("")
def list_cases():
    page = max(request.args.get("page", 1, type=int), 1)
    page_size = min(max(request.args.get("page_size", 10, type=int), 1), 100)
    keyword = request.args.get("keyword", "").strip()

    query = Case.query
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(or_(*(getattr(Case, field).like(pattern) for field in CASE_FIELDS)))

    pagination = query.order_by(Case.id.desc()).paginate(page=page, per_page=page_size, error_out=False)
    return response({
        "items": [item.to_dict() for item in pagination.items],
        "pagination": {
            "page": pagination.page,
            "page_size": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages,
        },
    })


@cases_bp.get("/<int:item_id>")
def get_case(item_id):
    item = db.get_or_404(Case, item_id)
    return response(item.to_dict())


@cases_bp.get("/options")
def get_case_options():
    options = grouped_options()
    return response({
        "projects": options["project"],
        "products": options["product"],
        "technologies": options["technology"],
    })


@cases_bp.get("/next-case-id")
def get_next_case_id():
    return response({"case_id": generate_case_id()})


@cases_bp.post("")
def create_case():
    payload, error = validate_case_payload(request.get_json(silent=True))
    if error:
        return response(None, error, 4001, 400)
    try:
        case_id = generate_case_id()
    except ValueError as error:
        return response(None, str(error), 4003, 409)
    item = Case(case_id=case_id, **payload)
    db.session.add(item)
    db.session.commit()
    return response(item.to_dict(), status=201)


@cases_bp.put("/<int:item_id>")
def update_case(item_id):
    item = db.get_or_404(Case, item_id)
    payload, error = validate_case_payload(request.get_json(silent=True))
    if error:
        return response(None, error, 4001, 400)
    for field, value in payload.items():
        setattr(item, field, value)
    db.session.commit()
    return response(item.to_dict())


@cases_bp.delete("/<int:item_id>")
def delete_case(item_id):
    item = db.get_or_404(Case, item_id)
    db.session.delete(item)
    db.session.commit()
    return response({"id": item_id})


@cases_bp.post("/batch-delete")
def batch_delete_cases():
    ids = (request.get_json(silent=True) or {}).get("ids", [])
    if not ids or not all(isinstance(item_id, int) and not isinstance(item_id, bool) and item_id > 0 for item_id in ids):
        return response(None, "ids must be a non-empty integer array", 4001, 400)
    deleted = Case.query.filter(Case.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    return response({"deleted": deleted})
