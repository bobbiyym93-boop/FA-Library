from datetime import datetime

from app.extensions import db
from app.models import Case


def generate_case_id(now=None):
    """Generate FA + YYYYMMDD + a three-digit daily sequence."""
    day = (now or datetime.now()).strftime("%Y%m%d")
    prefix = f"FA{day}"
    latest = (
        db.session.query(Case.case_id)
        .filter(Case.case_id.like(f"{prefix}%"))
        .order_by(Case.case_id.desc())
        .first()
    )
    sequence = int(latest[0][-3:]) + 1 if latest else 1
    if sequence > 999:
        raise ValueError("daily case id sequence exhausted")
    return f"{prefix}{sequence:03d}"
