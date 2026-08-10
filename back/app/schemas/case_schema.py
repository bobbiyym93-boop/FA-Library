CASE_FIELDS = ("case_id", "project", "product", "technology", "fail_type", "fail_model")


def validate_case_payload(payload):
    if not isinstance(payload, dict):
        return None, "request body must be a JSON object"

    result = {}
    for field in CASE_FIELDS:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            return None, f"{field} is required"
        result[field] = value.strip()
    return result, None
