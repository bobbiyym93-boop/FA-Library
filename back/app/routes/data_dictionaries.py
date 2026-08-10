from flask import Blueprint, request

from app.services.data_dictionary_service import grouped_options, replace_options


data_dictionaries_bp = Blueprint("data_dictionaries", __name__)


def response(data=None, message="success", code=0, status=200):
    return {"code": code, "message": message, "data": data}, status


@data_dictionaries_bp.get("")
def list_data_dictionaries():
    return response(grouped_options(include_items=True))


@data_dictionaries_bp.put("/<dictionary_type>")
def update_data_dictionary(dictionary_type):
    payload = request.get_json(silent=True) or {}
    try:
        items = replace_options(dictionary_type, payload.get("options"))
    except ValueError as error:
        return response(None, str(error), 4001, 400)
    return response(items)
