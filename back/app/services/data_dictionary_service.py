from app.extensions import db
from app.models import DataDictionaryOption


DICTIONARY_TYPES = ("project", "product", "technology")
DEFAULT_OPTIONS = {
    "project": ("Project1", "Project2", "Project3"),
    "product": ("Product1", "Product2", "Product3"),
    "technology": ("Technology1", "Technology2", "Technology3"),
}


def validate_dictionary_type(dictionary_type):
    if dictionary_type not in DICTIONARY_TYPES:
        raise ValueError(f"unsupported dictionary type: {dictionary_type}")
    return dictionary_type


def normalize_options(options):
    if not isinstance(options, list):
        raise ValueError("options must be an array")
    normalized = []
    for value in options:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("each option must be a non-empty string")
        value = value.strip()
        if len(value) > 100:
            raise ValueError("each option must not exceed 100 characters")
        if value in normalized:
            raise ValueError("options must not contain duplicates")
        normalized.append(value)
    return normalized


def ensure_default_options():
    existing_types = {
        item[0] for item in db.session.query(DataDictionaryOption.dictionary_type).distinct().all()
    }
    changed = False
    for dictionary_type, values in DEFAULT_OPTIONS.items():
        if dictionary_type in existing_types:
            continue
        for sort_order, value in enumerate(values):
            db.session.add(DataDictionaryOption(
                dictionary_type=dictionary_type,
                value=value,
                sort_order=sort_order,
            ))
        changed = True
    if changed:
        db.session.commit()


def grouped_options(include_items=False):
    rows = DataDictionaryOption.query.order_by(
        DataDictionaryOption.dictionary_type,
        DataDictionaryOption.sort_order,
        DataDictionaryOption.id,
    ).all()
    result = {dictionary_type: [] for dictionary_type in DICTIONARY_TYPES}
    for row in rows:
        result[row.dictionary_type].append(row.to_dict() if include_items else row.value)
    return result


def replace_options(dictionary_type, options):
    validate_dictionary_type(dictionary_type)
    values = normalize_options(options)
    DataDictionaryOption.query.filter_by(dictionary_type=dictionary_type).delete()
    for sort_order, value in enumerate(values):
        db.session.add(DataDictionaryOption(
            dictionary_type=dictionary_type,
            value=value,
            sort_order=sort_order,
        ))
    db.session.commit()
    return grouped_options(include_items=True)[dictionary_type]
