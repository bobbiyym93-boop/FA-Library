from datetime import datetime, timezone

from app.extensions import db


class DataDictionaryOption(db.Model):
    __tablename__ = "data_dictionary_options"
    __table_args__ = (
        db.UniqueConstraint("dictionary_type", "value", name="uq_dictionary_type_value"),
    )

    id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    dictionary_type = db.Column(db.String(30), nullable=False, index=True)
    value = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
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
            "dictionary_type": self.dictionary_type,
            "value": self.value,
            "sort_order": self.sort_order,
        }
