from datetime import datetime, timezone

from app.extensions import db


class Case(db.Model):
    __tablename__ = "fa_cases"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    case_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    project = db.Column(db.String(100), nullable=False, index=True)
    product = db.Column(db.String(100), nullable=False, index=True)
    technology = db.Column(db.String(100), nullable=False)
    fail_type = db.Column(db.String(100), nullable=False, index=True)
    fail_model = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "project": self.project,
            "product": self.product,
            "technology": self.technology,
            "fail_type": self.fail_type,
            "fail_model": self.fail_model,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
