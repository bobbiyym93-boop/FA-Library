CASE_FIELDS = ("case_id", "project", "product", "technology", "fail_type", "fail_model")
EDITABLE_FIELDS = ("project", "product", "technology", "fail_type", "fail_model")
REQUIRED_FIELDS = ("project", "product", "technology", "fail_model")
MAX_LENGTHS = {field: 100 for field in EDITABLE_FIELDS}


def validate_case_payload(payload):
    if not isinstance(payload, dict):
        return None, "request body must be a JSON object"

    result = {}
    unknown_fields = set(payload) - set(CASE_FIELDS)
    if unknown_fields:
        return None, f"unknown fields: {', '.join(sorted(unknown_fields))}"

    for field in REQUIRED_FIELDS:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            return None, f"{field} is required"
        value = value.strip()
        if len(value) > MAX_LENGTHS[field]:
            return None, f"{field} must not exceed {MAX_LENGTHS[field]} characters"
        result[field] = value

    fail_type = payload.get("fail_type")
    if fail_type is not None and not isinstance(fail_type, str):
        return None, "fail_type must be a string"
    fail_type = fail_type.strip() if fail_type else None
    if fail_type and len(fail_type) > MAX_LENGTHS["fail_type"]:
        return None, f"fail_type must not exceed {MAX_LENGTHS['fail_type']} characters"
    result["fail_type"] = fail_type
    return result, None
